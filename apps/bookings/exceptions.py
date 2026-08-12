class BookingException(Exception):
    pass

class BookingConflictException(BookingException):
    pass

class InvalidBookingDataException(BookingException):
    pass
