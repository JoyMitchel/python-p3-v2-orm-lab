from __init__ import CURSOR, CONN
from department import Department
from employee import Employee


class Review:

    # Dictionary of objects saved to the database.
    all = {}

    def __init__(self, year, summary, employee_id, id=None):
        self.id = id
        self.year = year
        self.summary = summary
        self.employee_id = employee_id

    def __repr__(self):
        return (
            f"<Review {self.id}: {self.year}, {self.summary}, "
            + f"Employee: {self.employee_id}>"
        )

    @classmethod
    def create_table(cls):
        """ Create a new table to persist the attributes of Review instances """
        sql = """
            CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY,
            year INT,
            summary TEXT,
            employee_id INTEGER,
            FOREIGN KEY (employee_id) REFERENCES employee(id))
        """
        CURSOR.execute(sql)
        CONN.commit()

    @classmethod
    def drop_table(cls):
        """ Drop the table that persists Review  instances """
        sql = """
            DROP TABLE IF EXISTS reviews;
        """
        CURSOR.execute(sql)
        CONN.commit()

    def save(self):
        """Insert a new row with the year, summary, and employee id values of the current Review object.
        Update object id attribute using the primary key value of new row.
        Save the object in local dictionary using table row's PK as dictionary key"""
        if self.id is None:
            # Insert a new review into the database
            sql = """
                INSERT INTO reviews (year, summary, employee_id)
                VALUES (?, ?, ?)
            """
            CURSOR.execute(sql, (self.year, self.summary, self.employee_id))
            CONN.commit()
            # Set the id to the primary key of the new row
            self.id = CURSOR.lastrowid
            # Add the instance to the all dictionary
            type(self).all[self.id] = self
        else:
            # If already in DB, update the row
            self.update()

    @classmethod
    def create(cls, year, summary, employee_id):
        """Initialize a new Review instance and save the object to the database. Return the new instance."""
        review = cls(year, summary, employee_id)  # Create new Review instance
        review.save()  # Save to DB
        return review  # Return the instance

    @classmethod
    def instance_from_db(cls, row):
        """Return a Review instance having the attribute values from the table row."""
        # row: (id, year, summary, employee_id)
        review = cls.all.get(row[0])  # Check if already in dictionary
        if review:
            # Update attributes in case they changed
            review.year = row[1]
            review.summary = row[2]
            review.employee_id = row[3]
        else:
            # Create new instance and add to dictionary
            review = cls(row[1], row[2], row[3], row[0])
            cls.all[review.id] = review
        return review

    @classmethod
    def find_by_id(cls, id):
        """Return a Review instance having the attribute values from the table row."""
        sql = "SELECT * FROM reviews WHERE id = ?"
        row = CURSOR.execute(sql, (id,)).fetchone()
        return cls.instance_from_db(row) if row else None

    def update(self):
        """Update the table row corresponding to the current Review instance."""
        sql = """
            UPDATE reviews
            SET year = ?, summary = ?, employee_id = ?
            WHERE id = ?
        """
        CURSOR.execute(sql, (self.year, self.summary, self.employee_id, self.id))
        CONN.commit()

    def delete(self):
        """Delete the table row corresponding to the current Review instance,
        delete the dictionary entry, and reassign id attribute"""
        sql = "DELETE FROM reviews WHERE id = ?"
        CURSOR.execute(sql, (self.id,))
        CONN.commit()
        # Remove from all dictionary
        del type(self).all[self.id]
        # Set id to None
        self.id = None

    @classmethod
    def get_all(cls):
        """Return a list containing one Review instance per table row"""
        sql = "SELECT * FROM reviews"
        rows = CURSOR.execute(sql).fetchall()
        return [cls.instance_from_db(row) for row in rows]

    # Property methods for validation

    @property
    def year(self):
        return self._year

    @year.setter
    def year(self, value):
        # Year must be int and >= 2000
        if isinstance(value, int) and value >= 2000:
            self._year = value
        else:
            raise ValueError("year must be an integer >= 2000")

    @property
    def summary(self):
        return self._summary

    @summary.setter
    def summary(self, value):
        # Summary must be a non-empty string
        if isinstance(value, str) and len(value.strip()) > 0:
            self._summary = value
        else:
            raise ValueError("summary must be a non-empty string")

    @property
    def employee_id(self):
        return self._employee_id

    @employee_id.setter
    def employee_id(self, value):
        # employee_id must reference an Employee in the database
        if type(value) is int:
            from employee import Employee
            if Employee.find_by_id(value):
                self._employee_id = value
                return
        raise ValueError("employee_id must reference an employee in the database")


