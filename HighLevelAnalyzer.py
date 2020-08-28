# High Level Analyzer
# For more information and documentation, please go to https://github.com/saleae/logic2-examples

from saleae.analyzers import HighLevelAnalyzer, AnalyzerFrame

commands = {
    b'\x00': ('Panel Setting (PSR)', 1),
    b'\x01': ('Power Setting (PWR)', 5),
    b'\x02': ('Power OFF (POF)', 0),
    b'\x04': ('Power ON (PON)', 0),
    b'\x06': ('Booster Soft Start (BTST)', 3),
    b'\x07': ('Deep sleep (DSLP)', 1),
    b'\x10': ('Display Start Transmission 1', 4736),
    b'\x12': ('Display Refresh (DRF) ', 1),
    b'\x13': ('Display Start Transmission 2', 4736),
    b'\x20': ('VCOM LUT (LUTC)', 44),
    b'\x21': ('W2W LUT (LUTWW)', 42),
    b'\x22': ('B2W LUT (LUTBW / LUTR)', 42),
    b'\x23': ('W2B LUT (LUTWB / LUTW)', 42),
    b'\x24': ('B2B LUT (LUTBB / LUTB)', 42),
    b'\x30': ('PLL control', 1),
    b'\x50': ('Vcom and data interval setting', 1),
    b'\x61': ('Resolution Setting', 3),
    b'\x71': ('Get Status', 0),
    b'\x82': ('VCM_DC Setting', 1),
    b'\x90': ('Partial Window (PTL)', 7),
    b'\x91': ('Partial In (PTIN)', 0)
}

first = True

class Hla(HighLevelAnalyzer):

    result_types = {
        'IL0373_frame': {
            'format': '{{data.command_id}}:{{data.command_name}} [{{data.command_data}}]'
        }
    }

    def __init__(self):
        '''
        Initialize this HLA.

        If you have any initialization to do before any methods are called, you can do it here.
        '''
        self._expecting_command = True


    def decode(self, frame):
        global first

        if first:
            print('-' * 5 + 'IL0373' + '-' * 5)
            first = False
        frame_complete = False

        if frame.type == "result":
            octet = frame.data['mosi']

            if self._expecting_command:
                command_id = octet
                self._remaining_data_len = commands[command_id][1]
                self._start_time = frame.start_time
                self._end_time = frame.end_time
                self._data = []
                if self._remaining_data_len > 0:
                    self._expecting_command = False
                else:
                    frame_complete = True

                self._command_name = commands[command_id][0]
                self._command_id = command_id
            else:
                self._remaining_data_len -= 1
                self._data.append(octet)
                self._end_time = frame.end_time
                if self._remaining_data_len == 0:
                    self._expecting_command = True
                    frame_complete = True

            if frame_complete:
                data_to_print = ",".join(map(str, self._data)) if len(self._data) < 6 else ''
                print(f'{self._command_name}({self._command_id}) data = [{data_to_print}]')
                return AnalyzerFrame(
                    'IL0373_frame',
                    self._start_time,
                    self._end_time,
                    {
                        'input_type': frame.type,
                        'command_id': self._command_id,
                        'command_name': self._command_name,
                        'command_data': data_to_print
                    }
                )
       
