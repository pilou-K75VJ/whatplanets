import json
import os
import shutil
import webbrowser


class RequestGenerator:
    def __init__(self, root_dir):
        self.root_dir = root_dir

        # noinspection SpellCheckingInspection
        self.base_config = {
            "COMMAND": None,
            "CENTER": "500@399",
            "MAKE_EPHEM": "YES",
            "TABLE_TYPE": "OBSERVER",
            "START_TIME": None,
            "STOP_TIME": None,
            "STEP_SIZE": None,
            "CAL_FORMAT": "CAL",
            "TIME_DIGITS": "MINUTES",
            "ANG_FORMAT": "DEG",
            "OUT_UNITS": "KM-S",
            "RANGE_UNITS": "AU",
            "APPARENT": "AIRLESS",
            "SUPPRESS_RANGE_RATE": "NO",
            "SKIP_DAYLT": "NO",
            "EXTRA_PREC": "NO",
            "R_T_S_ONLY": "NO",
            "REF_SYSTEM": "J2000",
            "CSV_FORMAT": "YES",
            "OBJ_DATA": "NO",
            "QUANTITIES": "31",
        }

        with open(os.path.join(root_dir, 'horizons_configuration.json'), 'r') as f:
            self.config = json.load(f)
        self.bodies = self.config['bodies'].keys()

    def write_batch_file(self, body):
        body_dir = os.path.join(self.root_dir, body)

        if os.path.exists(body_dir):
            shutil.rmtree(body_dir)
        os.makedirs(body_dir)

        with open(os.path.join(body_dir, 'batch-file.txt'), 'w') as batch_file:
            batch_file.write('!$$SOF\n')
            for k, v in self.base_config.items():
                if v is None:
                    if 'TIME' in k:
                        v = self.config['time_range'][k]
                    else:
                        v = self.config['bodies'][body][k]
                batch_file.write("{}= '{}'\n".format(k, v))
            batch_file.write('!$$EOF\n')
        print('Created {}'.format(batch_file.name))

    def open_email(self, body):
        body_dir = os.path.join(self.root_dir, body)

        email_url = "mailto:horizons@ssd.jpl.nasa.gov"
        email_url += "?subject=JOB {}".format(body)

        with open(os.path.join(body_dir, 'batch-file.txt'), 'r') as batch_file:
            email_url += "&body={}".format(''.join(batch_file.readlines()))

        email_url = email_url.replace(' ', '%20').replace('\n', '%0A')
        webbrowser.open(email_url)
        print('Email ready to be sent for {}'.format(body))

    def generate_all_requests(self):
        for body in self.bodies:
            self.write_batch_file(body)
            self.open_email(body)


if __name__ == '__main__':
    request_generator = RequestGenerator('./ecliptic_data/')
    request_generator.generate_all_requests()
