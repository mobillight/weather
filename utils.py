import csv
from datetime import datetime, date

DAY = 'day'
MONTH = 'month'


class NoMeasurements(Exception):
    pass


class Measurements:
    __slots__ = ('date', 'temperature', 'wind_speed', 'precipitation')

    def __init__(self, measurements_date: date, temperature: float, wind_speed: int, precipitation: float):
        self.date = measurements_date
        self.temperature = temperature
        self.wind_speed = wind_speed
        self.precipitation = precipitation


class MeasurementsParser:
    __slots__ = ('data',)

    _date_index = 0
    _temperature_index = 1
    _wind_speed_index = 7
    _precipitation_index = 23

    def __init__(self, data: str):
        self.data = data

    @staticmethod
    def parse_date(date_string: str):
        return datetime.strptime(date_string, '%d.%m.%Y %H:%M').date()

    @staticmethod
    def parse_precipitation(precipitation_value: str):
        try:
            return float(precipitation_value)
        except ValueError:
            return 0.0

    def get_date(self, source_row: str):
        try:
            return self.parse_date(source_row[self._date_index])
        except ValueError:
            raise NoMeasurements

    def parse(self):
        return Measurements(
            self.get_date(self.data),
            float(self.data[self._temperature_index]),
            int(self.data[self._wind_speed_index]),
            self.parse_precipitation(self.data[self._precipitation_index])
        )


class MeasurementsByPeriod:
    __slots__ = ('_temperature_sum', '_wind_speed_sum', '_updates_counter', 'date', 'precipitation', 'period')

    def __init__(self, measurements: Measurements, period: str):
        self._updates_counter = 1
        self._temperature_sum = measurements.temperature
        self._wind_speed_sum = measurements.wind_speed
        self.date = measurements.date
        self.precipitation = measurements.precipitation
        self.period = period

    def update(self, measurements: Measurements):
        self._updates_counter += 1
        self._temperature_sum += measurements.temperature
        self._wind_speed_sum += measurements.wind_speed
        self.precipitation += measurements.precipitation

    @property
    def temperature(self):
        return round(self._temperature_sum / self._updates_counter, 1)

    @property
    def wind_speed(self):
        return round(self._wind_speed_sum / self._updates_counter, 1)


class ResultMeasurements:
    hottest_day = None
    coldest_day = None
    hottest_month = None
    coldest_month = None

    def update_result_measurements(self, period_measurements: MeasurementsByPeriod):
        if period_measurements.period == DAY:
            self._update_day_measurements(period_measurements)
        elif period_measurements.period == MONTH:
            self._update_month_measurement(period_measurements)

    def _update_day_measurements(self, period_measurements: MeasurementsByPeriod):
        self._compare_hottest_day(period_measurements)
        self._compare_coldest_day(period_measurements)

    def _update_month_measurement(self, period_measurements: MeasurementsByPeriod):
        self._compare_hottest_month(period_measurements)
        self._compare_coldest_month(period_measurements)

    def _compare_hottest_day(self, period_measurements: MeasurementsByPeriod):
        # take last hottest day
        if self.hottest_day is None or self.hottest_day.temperature <= period_measurements.temperature:
            self.hottest_day = period_measurements

    def _compare_coldest_day(self, period_measurements: MeasurementsByPeriod):
        # take last coldest day
        if self.coldest_day is None or self.coldest_day.temperature >= period_measurements.temperature:
            self.coldest_day = period_measurements

    def _compare_hottest_month(self, period_measurements: MeasurementsByPeriod):
        # take last hottest month
        if self.hottest_month is None or self.hottest_month.temperature <= period_measurements.temperature:
            self.hottest_month = period_measurements

    def _compare_coldest_month(self, period_measurements: MeasurementsByPeriod):
        # take last coldest month
        if self.coldest_month is None or self.coldest_month.temperature >= period_measurements.temperature:
            self.coldest_month = period_measurements


class AggregateMeasurements:
    __slots__ = ('result_measurements', 'day_measurements', 'prev_day_measurements', 'month_measurements')

    def __init__(self):
        self.result_measurements = ResultMeasurements()
        self.day_measurements = None
        self.prev_day_measurements = None
        self.month_measurements = None

    @staticmethod
    def same_day_check(first: MeasurementsByPeriod, second: Measurements):
        return first.date == second.date

    @staticmethod
    def same_month_check(first: MeasurementsByPeriod, second: Measurements):
        return first.date.month == second.date.month and first.date.year == second.date.year

    def update_day_measurements(self, measurements: Measurements):
        if self.day_measurements is None:
            self.day_measurements = MeasurementsByPeriod(measurements, DAY)
        elif self.same_day_check(self.day_measurements, measurements):
            self.day_measurements.update(measurements)
            self.prev_day_measurements = None
        else:
            self.result_measurements.update_result_measurements(self.day_measurements)
            self.prev_day_measurements = self.day_measurements
            self.day_measurements = MeasurementsByPeriod(measurements, DAY)

    def update_month_measurements(self, measurements: Measurements):
        if self.month_measurements is None:
            self.month_measurements = MeasurementsByPeriod(measurements, MONTH)
        elif self.same_month_check(self.month_measurements, measurements):
            self.month_measurements.update(measurements)
        else:
            self.result_measurements.update_result_measurements(self.month_measurements)
            self.month_measurements = MeasurementsByPeriod(measurements, MONTH)

    def update_period_measurements(self, measurements: Measurements):
        self.update_day_measurements(measurements)
        if self.prev_day_measurements:
            self.update_month_measurements(self.prev_day_measurements)

    def update_all_measurements_by_period(self):
        self.result_measurements.update_result_measurements(self.day_measurements)
        self.result_measurements.update_result_measurements(self.month_measurements)


def process_file(filename: str):
    aggregate_measurements = AggregateMeasurements()
    with open(filename) as source_file:
        for row in csv.reader(source_file, delimiter=';'):
            try:
                measurements_by_time = MeasurementsParser(row).parse()
            except NoMeasurements:
                continue

            aggregate_measurements.update_period_measurements(measurements_by_time)
        aggregate_measurements.update_all_measurements_by_period()

    return aggregate_measurements.result_measurements
