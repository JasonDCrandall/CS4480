# This is the node in the network that will generate 100 messages 
# containing 512 bytes of data each. Once generated, it will send 
# the packets to node B, which will be approved by the router R.
#
# Created By: Jason Crandall u0726408

test = "sra <= 20 and dsa <= 20 and srp > 10 and dsp > 10"
sra = 0
dsa = 10
srp = 11 
dsp = 11
tmp = eval(test)
print(tmp)
test2 = "sra = 21;srp = 41"
tmp = exec(test2)
print(sra)
print(srp)
if("No Match Found"):
    print("hi")