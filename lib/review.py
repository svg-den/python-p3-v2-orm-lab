from __init__ import CURSOR, CONN
from department import Department
from employee import Employee

class Review:
    # Dictionary of objects saved to the database.
    all_reviews = {}

    def __init__(self, year, summary, employee_id, id=None):
        self.id = id
        self._year = None
        self.year = year
        self._summary = None
        self.summary = summary
        self.employee_id = employee_id
    
    @property
    def year(self):
        return self._year
    @year.setter
    def year(self, year):
        if isinstance(year, int) and year >= 2000:
            self._year = year
        else:
            raise ValueError("Year must be an integer")
    
    @property
    def summary(self):
        return self._summary
    
    @summary.setter
    def summary(self, summary):
        if isinstance(summary, str) and len(summary) > 0:
            self._summary = summary
        else:
            raise ValueError("Summary must be a non-empty string")
    
    @property
    def employee_id(self):
        return self._employee_id

    @employee_id.setter
    def employee_id(self, value):
        if isinstance(value, int) and Employee.find_by_id(value):
            self._employee_id = value
        else:
            raise ValueError("employee_id must be an integer corresponding to an existing employee")

    @classmethod
    def test_employee_fk_property_assignment(cls, employee_id):
        """Test method to check assignment of employee_id"""
        try:
            review = cls(year=2022, summary="Test summary", employee_id=employee_id)
            return True  
        except ValueError:
            return False  
        
    def _repr_(self):
        return f"<Review {self.id}: {self.year}, {self.summary}, Employee: {self.employee_id}>"

    
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
        """ Drop the table that persists Review instances """
        sql = """
            DROP TABLE IF EXISTS reviews;
        """
        CURSOR.execute(sql)
        CONN.commit()

    def save(self):
        """ Insert a new row with the year, summary, and employee id values of the current Review object.
        Update object id attribute using the primary key value of new row.
        Save the object in local dictionary using table row's PK as dictionary key"""
        sql = """
            INSERT INTO reviews (year, summary, employee_id)
            VALUES (?,?,?)
        """

        CURSOR.execute(sql, (self.year, self.summary, self.employee_id))
        CONN.commit()

        self.id = CURSOR.lastrowid
        type(self).all_reviews[self.id] = self

    @classmethod
    def create(cls, year, summary, employee_id):
        """ Initialize a new Review instance and save the object to the database. Return the new instance. """
        review = cls(year, summary, employee_id)
        review.save()
        return review

    @classmethod
    def instance_from_db(cls, row):
        """Create a Review instance from a database row."""
        review_id, year, summary, employee_id = row
        return cls(year, summary, employee_id, id=review_id)

    @classmethod
    def find_by_id(cls, id):
        """Return a Review instance having the attribute values from the table row."""
        sql = """
            SELECT * FROM reviews WHERE id = ?
        """

        row = CURSOR.execute(sql, (id,)).fetchone()
        return cls.instance_from_db(row) if row else None

    def update(self):
        """Update the table row corresponding to the current Review instance."""
        sql = """
            UPDATE reviews SET year = ?, summary = ? WHERE id = ?
        """
        CURSOR.execute(sql, (self.year, self.summary, self.id))
        CONN.commit()

    def delete(self):
        """Delete the table row corresponding to the current Review instance,
        delete the dictionary entry, and reassign id attribute"""
        sql = """
            DELETE FROM reviews WHERE id = ?
        """
        CURSOR.execute(sql, (self.id,))
        CONN.commit()
        del type(self).all_reviews[self.id]
        self.id = None

    @classmethod
    def get_all(cls):
        """Return a list containing one Review instance per table row"""
        sql = """
            SELECT * FROM reviews
        """

        rows = CURSOR.execute(sql).fetchall()
        return [cls.instance_from_db(row) for row in rows]

    def employees(self):
        """Return list of employees associated with current review"""
        sql = """
            SELECT * FROM employees WHERE id = ?
        """

        rows = CURSOR.execute(sql, (self.employee_id,)).fetchall()
        return [Employee.instance_from_db(row) for row in rows]

    def departments(self):
        """Return list of departments associated with current review"""
        sql = """
            SELECT * FROM departments WHERE id = ?
        """

        rows = CURSOR.execute(sql, (self.employee_id,)).fetchall()
        return [Department.instance_from_db(row) for row in rows]