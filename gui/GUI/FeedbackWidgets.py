from threading import Thread

from Logic import PcapLogic


class AsyncPcap2Bin(Thread):

    def __init__(self, master):
        Thread.__init__(self)
        self.master = master
        self.counter = 0

    def change_text(self):
        match self.counter:
            case 0:
                self.master.config(text="Analyzing Input buuble diagram .")
            case 1:
                self.master.config(text="Analyzing Input buuble diagram ..")
            case 2:
                self.master.config(text="Analyzing Input buuble diagram ...")
        self.counter += 1
        self.counter %= 3
        if PcapLogic.stop_pcap_bool:
            self.master.config(text="Finished generating floor plan")
            return
        self.master.after(1000, self.change_text)

    def run(self):
        self.master.after(0, self.change_text)
