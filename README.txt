CPSSchemas
==========

$Id$

This package adds a framework to deal with fields, schemas, widgets,
layouts and vocabularies, the way they are displayed to the user and the
way user input is validated.

Schemas define what's stored in an object, at the level of individual
fields. A field can be an integer, a string, a list of strings, a file
object, etc.

Vocabularies define an ordered list of options presented to the user and
the associated underlying values stored in the object. For instance a
list of countries where only country codes are stored but full country
names are displayed.

Widgets define how one or several fields from a schema are displayed to
the user. They can be displayed in several modes (typically "view" and
"edit"). Some modes may take input from the user and validate what the
user entered, so that if the entry is incorrect an appropriate message
can be displayed. Widgets can be parametrized and rewritten by the
administrator if a different widget is needed.

A Layout is a way to assemble several widgets together to display them.
A layout adds a level of graphical display that can for instance add
labels before the widgets, or borders, or display validation errors.
Layouts, like widgets, can be displayed in several modes.


The above talks about storing data in an object, but using a storage
adapter it is possible to do anything else with the data (sending it to
an SQL database, accumulating it for statistics, or just getting the
resulting dictionary for further treatment).
