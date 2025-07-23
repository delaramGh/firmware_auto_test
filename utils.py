from random import random
from datetime import datetime
import pandas as pd

class Tester:
    def __init__(self, log_file='log.log'):
        self.log_file = log_file

    def log(self, message):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(self.log_file, 'a') as f:
            f.write(f"[{timestamp}] {message}\n")

    def testLED(self):
        self.log("Testing LED")
        self.log("LED test completed")

    def testPower(self):
        self.log("Testing Power")
        self.log("Power test completed")

    def testPing(self):
        self.log("Testing Ping")
        self.log("Ping test completed")

    def testSensors(self, input_list):
        rx, tx, freq, bw = input_list
        if freq > 300000:
            boot_time = 9 + random() * 5
        else:
            boot_time = random() * 5

        if rx > -3 or tx > -3:
            temperature = 45 + random() * 10
        else:
            temperature = 25 + random() * 5
        
        if bw < 500:
            error_rate = random() * 15
        else:
            error_rate = random() * 5

        data_throughput = random()

        outputs = [round(boot_time, 3), round(temperature, 3), round(data_throughput, 3), round(error_rate, 3)]
        self.log(f"Testing Sensors: {input_list}")
        self.log(f"Sensor test completed: {outputs}")

    def getSensorLogs(self):
        input_columns = ["Rx Power (dBm)", "Tx Power (dBm)", "Frequency (GHz)", "Bandwidth (MHz)"]
        output_columns = ["Boot Time (s)", "Temperature (°C)", "Data Throughput (Mbps)", "Error Rate (%)"]
        try:
            input_list = []
            output_list = []
            with open(self.log_file, 'r') as f:
                for line in f:
                    ##  Read the 4 sensor numbers and store them as a list of lists
                    if "Testing Sensors" in line:
                        sensor_data = line.split(": ")[1].strip()[1:-1]  # Remove brackets
                        input_list.append([float(x) for x in sensor_data.split(',')])
                    ##  Read the 4 sensor outputs and store them as a list of lists
                    elif "Sensor test completed" in line:
                        sensor_outputs = line.split(": ")[1].strip()[1:-1]  # Remove brackets
                        output_list.append([float(x) for x in sensor_outputs.split(',')])

            input_df = pd.DataFrame(input_list, columns=input_columns)
            output_df = pd.DataFrame(output_list, columns=output_columns)
            return input_df, output_df
        except FileNotFoundError:
            print("Log file not found.")
            return pd.DataFrame(columns=input_columns), pd.DataFrame(columns=output_columns)


if __name__ == "__main__":
    tester = Tester()
    tester.testLED()
    tester.testPower()
    tester.testPing()
    tester.testSensors([1, 2, 3, 4])