from flask_wtf import FlaskForm
from wtforms import FloatField, SubmitField, StringField, PasswordField, SelectField
from wtforms.validators import DataRequired, NumberRange, EqualTo, Length

# Form for entering radioactive decay simulation parameters
class DecayForm(FlaskForm):
    # Dropdown menu to select a chemical element (populated dynamically)
    element = SelectField("Element", choices=[], coerce=int)

    # Field to enter the initial quantity N₀ (must be a positive float)
    n0 = FloatField("Initial quantity (N₀)", validators=[DataRequired(), NumberRange(min=0)])

    # Field to enter the elapsed time t (must be a positive float)
    t = FloatField("Elapsed time (t)", validators=[DataRequired(), NumberRange(min=0)])

    # Button to submit the form and trigger the simulation
    submit = SubmitField("Calculate")

# Form for user registration
class RegisterForm(FlaskForm):
    # Field to enter a username (minimum 3 characters)
    username = StringField("Username", validators=[DataRequired(), Length(min=3)])

    # Field to enter a password (minimum 6 characters)
    password = PasswordField("Password", validators=[DataRequired(), Length(min=6)])

    # Field to confirm the password (must match the first one)
    confirmation = PasswordField("Confirm Password", validators=[
        DataRequired(),
        EqualTo("password", message="Passwords must match.")
    ])

    # Button to submit the registration form
    submit = SubmitField("Register")

# Form for user login
class LoginForm(FlaskForm):
    # Field to enter the username
    username = StringField("Username", validators=[DataRequired(), Length(min=3)])

    # Field to enter the password
    password = PasswordField("Password", validators=[DataRequired(), Length(min=6)])

    # Button to submit the login form
    submit = SubmitField("Log In")

# Form for editing an existing simulation
class EditSimulationForm(FlaskForm):
    # Dropdown menu to select a new element (populated dynamically)
    element = SelectField("Element", choices=[], coerce=int)

    # Field to update the initial quantity N₀
    n0 = FloatField("Initial quantity (N₀)", validators=[DataRequired(), NumberRange(min=0)])

    # Field to update the elapsed time t
    t = FloatField("Elapsed time (t)", validators=[DataRequired(), NumberRange(min=0)])

    # Button to submit the updated simulation
    submit = SubmitField("Update")

# Form for changing the user's password
class ChangePasswordForm(FlaskForm):
    # Field to enter the current password
    current_password = PasswordField("Current Password", validators=[DataRequired()])

    # Field to enter the new password (minimum 6 characters, must match confirmation)
    new_password = PasswordField("New Password", validators=[
        DataRequired(),
        Length(min=6),
        EqualTo("confirm_password", message="Passwords must match.")
    ])

    # Field to confirm the new password
    confirm_password = PasswordField("Confirm New Password", validators=[DataRequired()])

    # Button to submit the password change request
    submit = SubmitField("Change Password")
