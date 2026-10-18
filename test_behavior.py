import unittest,struct
from midi_pedal_ledger import analyze,vlq,example
END=b'\0\xff\x2f\0'
def smf(*tracks,ppq=480,form=None):
 return b'MThd'+struct.pack('>IHHH',6,(0 if len(tracks)==1 else 1) if form is None else form,len(tracks),ppq)+b''.join(b'MTrk'+len(t).to_bytes(4,'big')+t for t in tracks)
ON=b'\0\x90\x3c\x50';OFF=vlq(480)+b'\x80\x3c\0'
class MidiTests(unittest.TestCase):
 def test_pedal_example(self):
  r=analyze(example());n=r['notes'][0];self.assertEqual((n['key_off_tick'],n['release_tick'],n['held_microseconds']),(480,960,'1000000'));self.assertEqual(n['release_cause'],'CC64_up');self.assertFalse(r['findings'])
 def test_default_tempo(self):self.assertEqual(analyze(smf(ON+OFF+END))['notes'][0]['held_microseconds'],'500000')
 def test_running_note_on_zero_is_off(self):
  n=analyze(smf(ON+vlq(480)+b'\x3c\0'+END))['notes'][0];self.assertEqual(n['release_tick'],480)
 def test_running_status_cleared_after_meta(self):
  with self.assertRaises(ValueError):analyze(smf(ON+b'\0\xff\x01\0'+vlq(480)+b'\x3c\0'+END))
 def test_tempo_fraction_is_exact(self):
  t=ON+vlq(1)+b'\xff\x51\x03'+(600000).to_bytes(3,'big')+vlq(1)+b'\x80\x3c\0'+END
  self.assertEqual(analyze(smf(t,ppq=3))['notes'][0]['held_microseconds'],'1100000/3')
 def test_format1_tempo_map(self):
  tempo=b'\0\xff\x51\x03'+(1000000).to_bytes(3,'big')+vlq(480)+b'\xff\x2f\0';r=analyze(smf(tempo,ON+OFF+END));self.assertEqual(r['notes'][0]['held_microseconds'],'1000000')
 def test_tempo_outside_track0(self):
  with self.assertRaises(ValueError):analyze(smf(END,b'\0\xff\x51\x03\x07\xa1\x20'+END))
 def test_cross_track_order_flag(self):
  r=analyze(smf(END,ON+END,b'\0\x80\x3c\0'+END));self.assertEqual(r['findings'][0]['reason'],'cross_track_same_tick_channel_order')
 def test_hanging_note_is_incomplete(self):
  r=analyze(smf(ON+vlq(480)+b'\xff\x2f\0'));self.assertEqual(r['notes'][0]['release_cause'],'capture_end');self.assertEqual(r['finding_count'],1)
 def test_unmatched_off(self):self.assertEqual(analyze(smf(OFF+END))['findings'][0]['reason'],'unmatched_note_off')
 def test_overlapping_key_refused(self):
  with self.assertRaises(ValueError):analyze(smf(ON+ON+OFF+END))
 def test_restrike_while_pedal_holds(self):
  t=ON+b'\0\xb0\x40\x7f'+OFF+ON+OFF+b'\0\xb0\x40\0'+END;r=analyze(smf(t));self.assertEqual(len(r['notes']),2);self.assertEqual(r['peak_serialized_held_voices'],2)
 def test_channel_pedal_is_independent(self):
  r=analyze(smf(ON+b'\0\xb1\x40\x7f'+OFF+END));self.assertEqual(r['notes'][0]['release_cause'],'key_off')
 def test_channel_modes_refused(self):
  for c in range(120,128):
   with self.assertRaises(ValueError):analyze(smf(bytes([0,176,c,0])+END))
 def test_sysex_and_unknown_meta_ignored(self):
  r=analyze(smf(b'\0\xf0\x02\x01\xf7\0\xff\x7f\x01\x01'+END));self.assertEqual(r['ignored_events'],{'meta_127':1,'sysex':1})
 def test_header_track_and_event_validation(self):
  for raw in [smf(ON+OFF+END,ppq=0),smf(END,ppq=0xe728),smf(END,form=2),smf(ON),smf(END+b'\0'),smf(b'\x81\x81\x81\x81\0'+END),smf(ON+OFF+END)+b'x',smf(ON+OFF+END)[:-1]]:
   with self.subTest(raw=raw),self.assertRaises(ValueError):analyze(raw)
 def test_tempo_validation(self):
  for t in [b'\0\xff\x51\x03\0\0\0',b'\0\xff\x51\x02\0\x01']:
   with self.assertRaises(ValueError):analyze(smf(t+END))
 def test_byte_budget(self):
  with self.assertRaises(ValueError):analyze(b'x'*(1024*1024+1))
if __name__=='__main__':unittest.main()
