from flask import Flask, flash, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os

load_dotenv()  # Reads from .env file

app = Flask(__name__)

# Using SQLite for student simplicity
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///rockbands-mm.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY') or 'SECRET'

db = SQLAlchemy(app)

# ==========================
# DATABASE MODELS
# ==========================


class Bands(db.Model):
    SingerID = db.Column(db.Integer, primary_key=True)
    SingerNane = db.Column(db.String(80), nullable=False)
    FormedYear = db.Column(db.Integer)
    HomeLocation = db.Column(db.String(80))
    # Relationship: One band has many members + albums
    # members = db.relationship('Members', backref='band', lazy=True)
    memberships = db.relationship('Memberships', backref='band', lazy=True)
    albumships = db.relationship('Albumships', backref='band', lazy=True)


class Members(db.Model):
    SongID = db.Column(db.Integer, primary_key=True)
    # SingerID = db.Column(db.Integer, db.ForeignKey('bands.SingerID'), nullable=False)
    SongNane = db.Column(db.String(80), nullable=False)
    SongArtist = db.Column(db.String(80))
    memberships = db.relationship('Memberships', backref='member', lazy=True)


class Memberships(db.Model):
    MembershipID = db.Column(db.Integer, primary_key=True)
    SingerID = db.Column(db.Integer, db.ForeignKey(
        'bands.SingerID'), nullable=False)
    SongID = db.Column(db.Integer, db.ForeignKey(
        'members.SongID'), nullable=False)
    StartYear = db.Column(db.Integer)
    Role = db.Column(db.Text)


class Albums(db.Model):
    AlbumID = db.Column(db.Integer, primary_key=True)
    # SingerID = db.Column(db.Integer, db.ForeignKey(
    #     'bands.SingerID'), nullable=False)
    AlbumTitle = db.Column(db.String(80), nullable=False)
    ReleaseYear = db.Column(db.Integer)
    albumships = db.relationship('Albumships', backref='albums', lazy=True)

class Albumships(db.Model):
    AlbumshipID = db.Column(db.Integer, primary_key=True)
    AlbumID = db.Column(db.Integer, db.ForeignKey(
        'albums.AlbumID'), nullable=False)
    SingerID = db.Column(db.Integer, db.ForeignKey(
        'bands.SingerID'), nullable=False)

# ==========================
# ROUTES
# ==========================


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/bands/add', methods=['GET', 'POST'])
def add_band():
    if request.method == 'POST':
        new_band = Bands(
            SingerNane=request.form['bandname'],
            FormedYear=request.form['formedyear'],
            HomeLocation=request.form['homelocation']
        )
        db.session.add(new_band)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('add_band.html')


@app.route('/members/add', methods=['GET', 'POST'])
def add_member():
    bands = Bands.query.all()  # Students see querying with relationships
    if request.method == 'POST':
        new_member = Members(
            SongNane=request.form['membername'],
            SongArtist=request.form['mainposition']
            # SingerID=request.form['bandid']
        )
        db.session.add(new_member)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('add_member.html', bands=bands)


@app.route('/albums/add', methods=['GET', 'POST'])
def add_album():
    bands = Bands.query.all()
    if request.method == 'POST':
        print(request.form)
        new_album = Albums(
            AlbumTitle=request.form['albumtitle'],
            ReleaseYear=request.form['releaseyear'],
        )
        db.session.add(new_album)
        db.session.commit()
        added_ids = []
        for key, value in request.form.items():
            if key.startswith("bandid") and value and not added_ids.__contains__(value):
                albumship = Albumships(
                    AlbumID = new_album.AlbumID,
                    SingerID = int(value),
                )
                added_ids.append(value)
                db.session.add(albumship)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('add_album.html', bands=bands)


@app.route('/bands/view')
def view_by_band():
    bands = Bands.query.all()
    return render_template('display_by_band.html', bands=bands)


@app.route('/bands/view/<int:id>')
def view_band(id):
    # Shows real database relationship querying
    band = Bands.query.get_or_404(id)
    return render_template('display_by_band.html', bands=[band])


@app.route('/memberships/add', methods=['GET', 'POST'])
def add_membership():
    bands = Bands.query.all()
    members = Members.query.all()
    if request.method == 'POST':
        membership = Memberships(
            SingerID=request.form.get('bandid'),
            SongID=request.form.get('memberid'),
            Role=request.form.get('role'),
            StartYear=request.form.get('startyear') or None
        )
        db.session.add(membership)
        db.session.commit()
        flash('Membership assigned', 'success')
        return redirect(url_for('view_by_band'))
    return render_template('add_membership.html', bands=bands, members=members)



@app.route('/memberships/edit/<int:id>', methods=['GET', 'POST'])
def edit_membership(id):
    membership = Memberships.query.get_or_404(id)
    bands = Bands.query.all()
    members = Members.query.all()
    if request.method == 'POST':
        membership.SingerID = request.form.get('bandid')
        membership.SongID = request.form.get('memberid')
        membership.Role = request.form.get('role')
        membership.StartYear = request.form.get('startyear') or None
        db.session.commit()
        flash('Membership updates', 'success')
        return redirect(url_for('view_by_band'))

    return render_template('edit_membership.html', membership=membership, bands=bands, members=members)


@app.route('/memberships/delete/<int:id>')
def delete_membership(id):
    membership = Memberships.query.get_or_404(id)
    db.session.delete(membership)
    db.session.commit()
    flash('Membership removed', 'success')
    return redirect(url_for('view_by_band'))


# Create DB if not exists
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
