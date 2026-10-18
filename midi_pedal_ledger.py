"""Reconstruct note/key/CC64 hold intervals and exact tempo time from bounded SMF."""
from __future__ import annotations
import argparse,bisect,hashlib,json,struct,sys
from collections import Counter,defaultdict
from fractions import Fraction
from pathlib import Path
MAX_BYTES=1024*1024
def vlq(value):
    if not 0<=value<=0x0fffffff:raise ValueError('VLQ range')
    out=[value&127];value>>=7
    while value:out.append((value&127)|128);value>>=7
    return bytes(reversed(out))
def example():
    track=b'\0\xff\x51\x03\x07\xa1\x20'+b'\0\x90\x3c\x50'+vlq(240)+b'\xb0\x40\x7f'+vlq(240)+b'\x80\x3c\0'+vlq(480)+b'\xb0\x40\0'+b'\0\xff\x2f\0'
    return b'MThd'+struct.pack('>IHHH',6,0,1,480)+b'MTrk'+len(track).to_bytes(4,'big')+track
def analyze(raw):
    if len(raw)>MAX_BYTES or len(raw)<14 or raw[:4]!=b'MThd' or int.from_bytes(raw[4:8],'big')!=6:raise ValueError('plain SMF header<=1MiB required')
    form,ntracks,ppq=struct.unpack_from('>HHH',raw,8)
    if form not in (0,1) or not 1<=ntracks<=16 or (form==0 and ntracks!=1) or not 1<=ppq<=32767:raise ValueError('format0/1, at most16 tracks and PPQ timing required; no SMPTE')
    offset=14;events=[];tempos={};end_ticks=[];ignored=Counter();total=0;collisions=defaultdict(set)
    for track in range(ntracks):
        if offset+8>len(raw) or raw[offset:offset+4]!=b'MTrk':raise ValueError('declared track chunk missing')
        size=int.from_bytes(raw[offset+4:offset+8],'big');offset+=8
        if offset+size>len(raw):raise ValueError('truncated track chunk')
        data=raw[offset:offset+size];offset+=size;pos=0;tick=0;running=None;ended=False;index=0
        def varint():
            nonlocal pos
            value=0
            for _ in range(4):
                if pos==len(data):raise ValueError('truncated VLQ')
                byte=data[pos];pos+=1;value=(value<<7)|(byte&127)
                if byte<128:return value
            raise ValueError('VLQ exceeds4bytes')
        while pos<len(data):
            tick+=varint();total+=1;index+=1
            if tick>10**9 or total>50000 or pos==len(data):raise ValueError('tick/event budget or missing status')
            status=data[pos]
            if status>=128:pos+=1
            elif running is None:raise ValueError('running data without channel status')
            else:status=running
            if status==255:
                running=None
                if pos==len(data):raise ValueError('missing meta type')
                kind=data[pos];pos+=1;length=varint()
                if pos+length>len(data):raise ValueError('truncated meta event')
                value=data[pos:pos+length];pos+=length
                if kind==47:
                    if length or pos!=len(data):raise ValueError('zero-length end-of-track must be final')
                    ended=True;break
                if kind==81:
                    if length!=3 or (form==1 and track!=0):raise ValueError('three-byte tempo on track0 required')
                    tempo=int.from_bytes(value,'big')
                    if not tempo or (tick in tempos and tempos[tick]!=tempo):raise ValueError('zero/conflicting same-tick tempo')
                    tempos[tick]=tempo
                else:ignored['meta_'+str(kind)]+=1
            elif status in (240,247):
                running=None;length=varint()
                if pos+length>len(data):raise ValueError('truncated sysex event')
                pos+=length;ignored['sysex']+=1
            elif 128<=status<=239:
                running=status;kind=status>>4;channel=status&15;length=1 if kind in (12,13) else 2
                if pos+length>len(data) or any(v>=128 for v in data[pos:pos+length]):raise ValueError('truncated/non-data channel bytes')
                value=data[pos:pos+length];pos+=length
                if kind==11 and value[0]>=120:raise ValueError('channel-mode/reset/all-notes-off controllers unsupported')
                if kind in (8,9) or (kind==11 and value[0]==64):
                    event={'tick':tick,'track':track,'index':index,'channel':channel,'kind':'on' if kind==9 and value[1] else 'off' if kind in (8,9) else 'pedal','a':value[0],'b':value[1]};events.append(event);collisions[(tick,channel)].add(track)
                else:ignored['channel_'+str(kind)]+=1
            else:raise ValueError('unsupported system event in SMF')
        if not ended:raise ValueError('track lacks end-of-track event')
        end_ticks.append(tick)
    if offset!=len(raw):raise ValueError('extra bytes/chunks after declared tracks')
    end=max(end_ticks);events.sort(key=lambda e:(e['tick'],e['track'],e['index']));notes=[];active={};pending=defaultdict(list);pedals=defaultdict(bool);findings=[];held=0;peak=0
    ambiguous=[{'tick':tick,'channel':ch,'tracks':sorted(tracks)} for (tick,ch),tracks in sorted(collisions.items()) if len(tracks)>1]
    if ambiguous:findings.append({'reason':'cross_track_same_tick_channel_order','count':len(ambiguous)})
    def close(note,tick,cause):
        nonlocal held
        note['release_tick']=tick;note['release_cause']=cause;held-=1
    for e in events:
        ch=e['channel'];key=(ch,e['a']);tick=e['tick']
        if e['kind']=='on':
            if key in active:raise ValueError('overlapping key-down note of same channel/pitch unsupported')
            if len(notes)>=20000:raise ValueError('note budget20000')
            note={'note':len(notes)+1,'channel':ch,'pitch':e['a'],'velocity':e['b'],'on_track':e['track'],'on_tick':tick,'key_off_tick':None,'release_tick':None};notes.append(note);active[key]=note;held+=1;peak=max(peak,held)
        elif e['kind']=='off':
            note=active.pop(key,None)
            if note is None:findings.append({'reason':'unmatched_note_off','tick':tick,'channel':ch,'pitch':e['a']})
            else:
                note['key_off_tick']=tick
                if pedals[ch]:pending[ch].append(note)
                else:close(note,tick,'key_off')
        else:
            down=e['b']>=64
            if pedals[ch] and not down:
                for note in pending[ch]:close(note,tick,'CC64_up')
                pending[ch]=[]
            pedals[ch]=down
    unfinished=list(active.values())+[n for group in pending.values() for n in group]
    for note in unfinished:close(note,end,'capture_end');findings.append({'reason':'held_at_capture_end','note':note['note']})
    if held!=0:raise ValueError('internal held-voice accounting mismatch')
    tempos.setdefault(0,500000);ticks=sorted(tempos);cumulative=[Fraction(0)]
    for a,b in zip(ticks,ticks[1:]):cumulative.append(cumulative[-1]+Fraction((b-a)*tempos[a],ppq))
    def micros(t):
        i=bisect.bisect_right(ticks,t)-1;return cumulative[i]+Fraction((t-ticks[i])*tempos[ticks[i]],ppq)
    for note in notes:
        note['on_microseconds']=str(micros(note['on_tick']));note['release_microseconds']=str(micros(note['release_tick']));note['held_microseconds']=str(micros(note['release_tick'])-micros(note['on_tick']));note['held_ticks']=note['release_tick']-note['on_tick']
    return {'source_sha256':hashlib.sha256(raw).hexdigest(),'format':form,'ppq':ppq,'track_end_ticks':end_ticks,'capture_end_tick':end,'tempo_changes':[{'tick':t,'microseconds_per_quarter':tempos[t]} for t in ticks],'notes':notes,'peak_serialized_held_voices':peak,'findings':findings[:512],'finding_count':len(findings),'omitted_findings':max(0,len(findings)-512),'cross_track_order_evidence':ambiguous[:256],'ignored_events':dict(sorted(ignored.items())),
      'scope':'Key plus CC64 hold ledger, not audible duration or synthesis. Exact microseconds are integer or numerator/denominator strings. Format1 tempo must be on track0. Events serialize by tick,track,event index; same-channel cross-track simultaneous events are flagged. Other controls/programs are ignored; channel-mode controllers rejected. Capture-end closures are incomplete evidence, not observed note releases.'}
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('input',nargs='?');p.add_argument('--make-example',metavar='NEW_FILE');a=p.parse_args()
    try:
        if a.make_example:
            if a.input:raise ValueError('choose input or example creation')
            with Path(a.make_example).open('xb') as f:f.write(example())
            print(json.dumps({'example':a.make_example,'source':'invented MIDI events'}));return 0
        if not a.input:raise ValueError('MIDI path required')
        with Path(a.input).open('rb') as f:raw=f.read(MAX_BYTES+1)
        r=analyze(raw);print(json.dumps(r,sort_keys=True,indent=2));return int(bool(r['finding_count']))
    except (ValueError,OSError,UnicodeError,struct.error,OverflowError) as e:print(json.dumps({'error':str(e)}),file=sys.stderr);return 2
if __name__=='__main__':raise SystemExit(main())
