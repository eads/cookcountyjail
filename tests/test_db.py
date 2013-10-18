#!/usr/bin/env python

from ccj.app import app
from ccj.app import db
from fabric.api import local

def prep_db():
    # make sure PostgreSQL DB is being used
    db_string = app.config['SQLALCHEMY_DATABASE_URI']
    if db_string.find('postgresql') == -1:
        raise Exception('Make sure CCJ_PRODUCTION is set')


def add_data():
    # Declare a model
    class ElaborateTest(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        test_string = db.Column(db.String)
        def __init__(self, test):
            self.test_string = test
        def __repr__(self):
            return '<Test %r>' % self.test_string

    # Add some new data to the DB
    db.create_all()
    one = ElaborateTest('first')
    two = ElaborateTest('second')
    db.session.add(one)
    db.session.add(two)
    db.session.commit()


def check_result():
    # Check if 'elaborate_test' table is now in DB
    result = local('psql cookcountyjail_v2_0_dev -c "\dt"', capture=True)
    assert result.find('elaborate_test') != -1


def undo_changes():
    # Clean up table we created in the test
    local('psql cookcountyjail_v2_0_dev -c "DROP TABLE elaborate_test;"', capture=True)


def test_db_available():
    add_data()
    check_result()


test_db_available.setUp = prep_db
test_db_available.tearDown = undo_changes