from typing import Optional

from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column



class Base(DeclarativeBase):
    pass

class Bookings(Base):
    __tablename__ = 'bookings'

    booking_no : Mapped[str] = mapped_column(String(12), primary_key=True)
    cancellation : Mapped[Optional[str]] = mapped_column(String(255))
    revised_no : Mapped[int]
    booking_in_navis : Mapped[int]
    date_booked : Mapped[Optional[str]] = mapped_column(String(255))
    etd : Mapped[Optional[str]] = mapped_column(String(255))
    navis_voy : Mapped[Optional[str]] = mapped_column(String(255))
    pod : Mapped[Optional[str]] = mapped_column(String(255))
    tod : Mapped[Optional[str]] = mapped_column(String(255))
    ocean_vessel : Mapped[Optional[str]] = mapped_column(String(255))
    voyage : Mapped[Optional[str]] = mapped_column(String(255))
    final_dest : Mapped[Optional[str]] = mapped_column(String(255))
    commodity : Mapped[Optional[str]] = mapped_column(String(255))
    count_40hc : Mapped[int]
    count_40dv : Mapped[int]
    count_20dv : Mapped[int]
    weight_40hc : Mapped[int]
    weight_40dv : Mapped[int]
    weight_20dv : Mapped[int]
    hazard_40hc : Mapped[Optional[str]] = mapped_column(String(255))
    hazard_40dv : Mapped[Optional[str]] = mapped_column(String(255))
    hazard_20dv : Mapped[Optional[str]] = mapped_column(String(255))
    pdf_name : Mapped[Optional[str]] = mapped_column(String(1000))

    def __repr__(self):
        return f'<Booking {self.booking_no}>'