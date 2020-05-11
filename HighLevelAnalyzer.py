# High Level Analyzer
# For more information and documentation, please go to https://github.com/saleae/logic2-examples

commands = {
    0x00: ('Panel Setting', 2),
    0x01: ('Power Setting', 5),
    0x04: ('Power ON', 0),
    0x06: ('Booster Soft Start', 3),
    0x30: ('PLL control', 1),
    0x61: ('Resolution Setting', 3),
    0x71: ('Get Status', 0),
    0x82: ('VCM_DC Setting', 1),
}
class Hla():

    def __init__(self):
        '''
        Initialize this HLA.

        If you have any initialization to do before any methods are called, you can do it here.
        '''
        self._command = True

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
                'IL0373_command': {
                    'format': '{{data.command_name}}({{data.command_id}})'
                },
                'IL0373_data': {
                    'format': 'data = {{data.data}}'
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

        octet = frame['data']['mosi']

        if self._command:
            command_id = octet
            self._remaining_data_len = commands[command_id][1]
            if self._remaining_data_len > 0:
                self._command = False
            return {
                'type': 'IL0373_command',  # This type matches up with the type returned from `set_settings`
                'start_time': frame['start_time'],
                'end_time': frame['end_time'],
                'data': {
                    'input_type': frame['type'],
                    'command_id': hex(command_id),
                    'command_name': commands[command_id][0]
                }
            }
        else:
            self._remaining_data_len -= 1
            if self._remaining_data_len == 0:
                self._command = True

            return {
                'type': 'IL0373_data',  # This type matches up with the type returned from `set_settings`
                'start_time': frame['start_time'],
                'end_time': frame['end_time'],
                'data': {
                    'input_type': frame['type'],
                    'data': hex(octet)
                }
            }
       
