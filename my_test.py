import unittest
from main import *

# Add imports here!
import os

class UnitTests(unittest.TestCase):

  # Add initialization code here!

  def setUp(self):
      # Add setup code here!
      self.used_files = []
      self.n = 114823184016855280547837108252858991818182128357824343857742678840558068456105823410138410671169557249152804868781125462604111071001214193071175814610089060963049327236706378556907983266446954983629718925983414432950400324037386131571488229511953759140593170292646194976289028827063298570003501242765211451513
      self.e=65537
      self.d = 4944902634993544447200844689338280620608843623051321886804347058800678677064889655418914457757330655066262533248792727429044325861987150894445272743032944030680377871726007592717693372124068696068141722668478540920130935226077647322131436667632948467024781747615159717863877120261484024549157281019831831825
      self.u = User()
      self.u._public['e'] = self.e
      self.u._public['n'] = self.n
      self.u._private['d'] = self.d
      self.u._private['n'] = self.n
      self.genesis = self.u.build_transaction(float('inf'), self.u)
      self.chain = Blockchain(self.genesis, pow_hardness=1)

  def tearDown(self):
      # Add teardown code here!
      for f in self.used_files:
        if os.path.exists(f):
          os.remove(f)
      os.system('cp %s ./my_test.py' % os.path.abspath(__file__))

  def test_check_chain(self):
      u1 = User()
      t1 = self.u.build_transaction(100, u1)
      self.chain.submit_transaction(t1)
      t2 = self.u.build_transaction(70, u1)
      self.chain.submit_transaction(t2)
      self.chain.build_block()
      self.assertTrue(self.chain.check_chain())

  def test_build_block(self):
      u1 = User()
    
      l = len(self.chain._chain)
      
      t1 = self.u.build_transaction(100, u1)
      self.chain.submit_transaction(t1)
      self.chain.build_block()
      self.assertEquals(len(self.chain._chain), l+1)

  def test_balance_updated(self):
      u1 = User()
    
      u1.update_balance(self.chain)
      self.assertEquals(u1._account_balance, 0)
      
      t1 = self.u.build_transaction(100, u1)
      self.chain.submit_transaction(t1)
      u1.update_balance(self.chain)
      self.assertEquals(u1._account_balance, 100)
    
      t2 = u1.build_transaction(70, self.u)
      self.chain.submit_transaction(t2)
      u1.update_balance(self.chain)
      self.assertEquals(u1._account_balance, 30)
    
      t3 = u1.build_transaction(50, self.u)
      self.chain.submit_transaction(t3)
      u1.update_balance(self.chain)
      self.assertEquals(u1._account_balance, 30)

  def test_submit_transactions(self):
      u1 = User()
      u2 = User()
      l = len(self.chain._pending)
      
      t1 = self.u.build_transaction(100, u1)
      r = self.chain.submit_transaction(t1)
      self.assertTrue(r)
      self.assertEquals(len(self.chain._pending), l+1)
      
      t2 = self.u.build_transaction(200, u2)
      r = self.chain.submit_transaction(t2)
      self.assertTrue(r)
      self.assertEquals(len(self.chain._pending), l+2)
    
      t3 = u1.build_transaction(50, u2)
      r = self.chain.submit_transaction(t3)
      self.assertTrue(r)
      self.assertEquals(len(self.chain._pending), l+3)
    
      t4 = u1.build_transaction(60, u2)
      r = self.chain.submit_transaction(t4)
      self.assertFalse(r)
      self.assertEquals(len(self.chain._pending), l+3)
    
      u3 = User()
      t5 = u3.build_transaction(60, u1)
      r = self.chain.submit_transaction(t5)
      self.assertFalse(r)
      self.assertEquals(len(self.chain._pending), l+3)

  def test_save_and_load_blockchain(self):
      file_name = 'test_c.json'
      self.used_files.append(file_name)
      
      self.assertRaises(Exception, open, file_name)
      self.chain.write_to_file(file_name)
      o = Blockchain(file=file_name)
      self.assertDictEqual(self.chain.__dict__, o.__dict__)
    

  def test_blockchain_created(self):
      self.assertRaises(AssertionError, Blockchain)
      c = Blockchain(self.genesis, pow_hardness=1)
      self.assertTrue(c)

  def test_can_verify_transaction(self):
      msg = "%s test" % self.u.public()
      t = "%s %s" % (msg, self.u.sign(msg))
      self.assertTrue(verify_transaction(t))
      

  def test_can_sign(self):
      sign = self.u.sign("test")
      self.assertEquals(sign, "50a372260ca57a5a12504f5e20f490b7869236af76714f91656a11ae1e09faeac0c7ee276f86153e9a725f30769872cd5bd1013394607350b64817c101fd794802d8450f6c80b3a64f144d8732c84fed21c1ad32ef149dcec0b8e6afed5ecd3b7d2f3b9882ea1f6576fcc2bd7156925dc7e5f9d0e7e834bf8b9e87bb8570805c")

  def test_valid_transaction(self):
      t = self.u.build_transaction(5.5, 'test')
      self.assertTrue(verify_transaction(t))

  def test_get_public_private_keys(self):
      u = User()
      u._public['e'] = 1
      u._public['n'] = 10
      u._private['d'] = 3
      u._private['n'] = 11
      self.assertEqual(u.public(), "1-a")
      self.assertEqual(u.private(), "3-b")

  def test_save_and_load_user(self):
      file_name = 'test_u.json'
      self.used_files.append(file_name)
      
      self.assertRaises(Exception, open, file_name)
      self.u.write_to_file(file_name)
      o = User(file_name)
      self.assertDictEqual(self.u.__dict__, o.__dict__)
    

  def test_user_created(self):
      u = User()
      self.assertTrue(u)

