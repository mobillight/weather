from utils import process_file, ResultMeasurements


def print_results(result_measurements: ResultMeasurements):
    print(f'Hottest day is {result_measurements.hottest_day.date} with temperature '
          f'{result_measurements.hottest_day.temperature}')
    print(f'Coldest day is {result_measurements.coldest_day.date} with temperature '
          f'{result_measurements.coldest_day.temperature}')
    print(f'Hottest month is {result_measurements.hottest_month.date.strftime("%Y-%m")} with temperature '
          f'{result_measurements.hottest_month.temperature}')
    print(f'Coldest month is {result_measurements.coldest_month.date.strftime("%Y-%m")} with temperature '
          f'{result_measurements.coldest_month.temperature}')


if __name__ == '__main__':
    filename = '34300.01.01.2016.01.01.2017.1.0.0.ru.csv'
    print_results(process_file(filename))
