"""1.Class contains functions which are used to analyze pcap files.
   2.Class contains structures to save data from pcap->bin files."""
from datetime import datetime
from threading import Thread
import time

#import pandas as pd
#import pyshark
#from pandas import DataFrame

# parsed_xml_df = DataFrame
# deciphered_bin_df = DataFrame
stop_pcap_bool = False


class AsyncPcap2Bin(Thread):
    """Class AsyncConvert(Thread) converts .pcapng to .binary and saves it to the same location of the original."""

    def __init__(self, path, dest_port, message_label):
        super().__init__()
        self.path = path
        self.message_label = message_label
        self.dest_port = dest_port
        # self.packets = pyshark.FileCapture(input_file=self.path, display_filter=f"udp.dstport=={dest_port}")
        # self.binary_packet = bytearray()

    def run(self):
        global stop_pcap_bool, deciphered_bin_df
        stop_pcap_bool = False
        # start = datetime.now()
        # dct = {}
        # i=0
        
        #make thread sleep for 10 seconds
        time.sleep(1)

        # for pkt in self.packets:
        #     if i == 100: #debug
        #         break
        #     i+=1
        #     mystring = pkt.dns.qry_name.split('.')[1]
        #     mystring = f'{mystring}'
        #     if mystring in dct:
        #         val = dct.get(mystring)
        #         dct[mystring] = val + 1
        #     else:
        #         dct[mystring] = 1

        # deciphered_bin_df = pd.DataFrame(dct, index=[0])
        # deciphered_bin_df.to_csv('deciphered_data.csv')
        stop_pcap_bool = True
        # end = datetime.now()
        # print("Pcap2Values: ", end - start)


if __name__ == '__main__':
    thread = AsyncPcap2Bin(path=r'C:\Users\97254\Desktop\mergedPcap.pcapng',
                           dest_port='53',
                           message_label=None)
    thread.start()
