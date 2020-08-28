# High Level Analyzer
# For more information and documentation, please go to https://github.com/saleae/logic2-examples

commands = {
    0x00: ('Panel Setting (PSR)', 1),
    0x01: ('Power Setting (PWR)', 5),
    0x02: ('Power OFF (POF)', 0),
    0x04: ('Power ON (PON)', 0),
    0x06: ('Booster Soft Start (BTST)', 3),
    0x07: ('Deep sleep (DSLP)', 1),
    0x10: ('Display Start Transmission 1', 4736),
    0x12: ('Display Refresh (DRF) ', 1),
    0x13: ('Display Start Transmission 2', 4736),
    0x20: ('VCOM LUT (LUTC)', 44),
    0x21: ('W2W LUT (LUTWW)', 42),
    0x22: ('B2W LUT (LUTBW / LUTR)', 42),
    0x23: ('W2B LUT (LUTWB / LUTW)', 42),
    0x24: ('B2B LUT (LUTBB / LUTB)', 42),
    0x30: ('PLL control', 1),
    0x50: ('Vcom and data interval setting', 1),
    0x61: ('Resolution Setting', 3),
    0x71: ('Get Status', 0),
    0x82: ('VCM_DC Setting', 1),
    0x90: ('Partial Window (PTL)', 7),
    0x91: ('Partial In (PTIN)', 0)
}

first = True

class Hla():

    def __init__(self):
        '''
        Initialize this HLA.

        If you have any initialization to do before any methods are called, you can do it here.
        '''
        self._expecting_command = True

    def get_capabilities(self):
        '''
        Return the settings that a user can set for this High Level Analyzer. The settings that a user selects will later be passed into `set_settings`.

        This method will be called first, before `set_settings` and `decode`
        '''

        return {
            'settings': {
            }
        }

    def set_settings(self, settings):
        '''
        Handle the settings values chosen by the user, and return information about how to display the results that `decode` will return.

        This method will be called second, after `get_capbilities` and before `decode`.
        '''


        # Here you can specify how output frames will be formatted in the Logic 2 UI
        # If no format is given for a type, a default formatting will be used
        # You can include the values from your frame data (as returned by `decode`) by wrapping their name in double braces, as shown below.
        return {
            'result_types': {
                'IL0373_frame': {
                    'format': '{{data.command_id}}:{{data.command_name}} [{{data.command_data}}]'
                }
            }
        }

    def decode(self, frame):
        '''
        Handle data frame from input analyzer.

        `frame` will always be of the form:

        {
            'type': 'FRAME_TYPE'
            'start_time': ...,
            'end_time': ...,
            'data': {
                ...
            }
        }

        The `type` and contents of the `data` field will depend on the input analyzer.
        '''
        global first

        if first:
            print('-' * 5 + 'IL0373' + '-' * 5)
            first = False
        frame_complete = False

        octet = frame['data']['mosi']

        if self._expecting_command:
            command_id = octet
            self._remaining_data_len = commands[command_id][1]
            self._start_time = frame['start_time']
            self._end_time = frame['end_time']
            self._data = []
            if self._remaining_data_len > 0:
                self._expecting_command = False
            else:
                frame_complete = True

            self._command_name = commands[command_id][0]
            self._command_id = hex(command_id)
        else:
            self._remaining_data_len -= 1
            self._data.append(hex(octet))
            self._end_time = frame['end_time']
            if self._remaining_data_len == 0:
                self._expecting_command = True
                frame_complete = True

        if frame_complete:
            data_to_print = ",".join(self._data) if len(self._data) < 6 else None
            print(f'{self._command_name}({self._command_id}) data = [{data_to_print}]')
            return {
                'type': 'IL0373_frame',  # This type matches up with the type returned from `set_settings`
                'start_time': self._start_time,
                'end_time': self._end_time,
                'data': {
                    'input_type': frame['type'],
                    'command_id': self._command_id,
                    'command_name': self._command_name,
                    'command_data': ",".join(self._data)
                }
            }

        return None
       
