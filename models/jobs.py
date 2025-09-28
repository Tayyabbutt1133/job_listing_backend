from db import db
from datetime import datetime, timezone


class Job(db.Model):
    __tablename__ = "jobs"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    company = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    posting_date = db.Column(
        db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    job_type = db.Column(db.String(50), nullable=False)
    tags = db.Column(db.Text, nullable=True)

    def __init__(
        self, title, company, location, posting_date=None, job_type=None, tags=None
    ):
        self.title = title
        self.company = company
        self.location = location
        if posting_date is not None:  # only set if user provides one
            self.posting_date = posting_date
        self.job_type = job_type
        self.tags = tags
