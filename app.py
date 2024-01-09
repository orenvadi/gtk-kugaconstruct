import decimal

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
import psycopg2
from gi.repository import Adw, Gtk


class MainWindow(Gtk.ApplicationWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class DatabaseApp(Adw.Application):
    def __init__(self, *args, **kwargs):
        super().__init__(
            *args,
            application_id="org.example.MyDatabaseApp",
            **kwargs,
        )
        self.connect("activate", self.do_activate)

    def do_activate(self, *args, **kwargs):
        # if not self.window:
        self.window = MainWindow(application=app)
        self.window.set_default_size(600, 550)
        self.window.set_title("KugaConstruct")

        # self.window = Adw.ApplicationWindow(application=self)
        self.init_ui()
        self.window.present()

    def init_ui(self):
        # Configuration for your database
        db_config = {
            "dbname": "kugaconstruct",
            "user": "postgres",
            "password": "postgres",
            "host": "127.0.0.1",
        }

        # Connect to the database
        conn = psycopg2.connect(**db_config)
        cur = conn.cursor()

        # Get the list of tables
        cur.execute(
            "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"
        )
        tables = cur.fetchall()

        # Create a notebook (tabs container)
        notebook = Gtk.Notebook()
        self.window.set_child(notebook)

        # Create a tab for each table
        for table in tables:
            tab_label = Gtk.Label(label=table[0])

            # Create a scrolled window to contain the TreeView
            scrolled_window = Gtk.ScrolledWindow()

            scrolled_window.set_hexpand(
                True,
            )
            scrolled_window.set_vexpand(
                True,
            )  # Make the scrolled window expand vertically
            scrolled_window.set_policy(
                Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC
            )

            # Create a TreeView for the table and add it to the scrolled window
            treeview = create_treeview_for_table(table[0], cur)
            scrolled_window.set_child(treeview)

            # Create a button box for Add/Delete operations
            button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
            button_box.set_layout_manager(
                Gtk.BoxLayout(orientation=Gtk.Orientation.HORIZONTAL),
            )
            button_box.set_halign(Gtk.Align.CENTER)
            button_box.set_valign(Gtk.Align.END)
            button_box.set_spacing(10)  # Adds some space between the buttons

            # Create Add/Delete buttons
            add_button = Gtk.Button(label="Add")
            delete_button = Gtk.Button(label="Delete")

            # Add buttons to the button box
            button_box.append(add_button)
            button_box.append(delete_button)

            # Connect the buttons to their respective callback functions
            delete_button.connect(
                "clicked",
                lambda w, tv=treeview, tn=table[0]: on_delete_button_clicked(
                    tv,
                    tn,
                ),
            )
            add_button.connect(
                "clicked",
                lambda w, tv=treeview, tn=table[0]: on_add_button_clicked(
                    tv,
                    tn,
                ),
            )

            main_vbox = Gtk.Box(
                orientation=Gtk.Orientation.VERTICAL,
                spacing=6,
            )
            main_vbox.append(
                scrolled_window
            )  # The scrolled window should expand to fill the space
            main_vbox.append(button_box)  # The button box should remain at the bottom

            # Add the main vbox to the notebook as a new page
            notebook.append_page(main_vbox, tab_label)

        # Ensure that the cursor and connection are closed properly after use
        cur.close()
        conn.close()


def create_treeview_for_table(table_name, cur):
    # Query to get all data from the table
    cur.execute(f"SELECT * FROM {table_name}")

    # Determine the types for each column
    column_types = get_column_types(cur)

    # Creating a ListStore with the correct types for each column
    store = Gtk.ListStore(*column_types)

    # Filling the ListStore with the rows from the table
    for row in cur.fetchall():
        # Ensure all values are converted to the appropriate type
        converted_row = [
            col_type(val)
            for col_type, val in zip(
                column_types,
                row,
            )
        ]
        store.append(converted_row)

    # Creating the TreeView and adding the columns
    treeview = Gtk.TreeView(model=store)
    for i, col_name in enumerate([desc[0] for desc in cur.description]):
        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn(col_name, renderer, text=i)
        treeview.append_column(column)

    return treeview


def get_column_types(cur):
    """
    This function returns a tuple of types for the columns in current query.
    It should be called right after executing a SELECT query.
    """
    # Fetch one row from the query
    example_row = cur.fetchone()
    # Return to the start of the results
    cur.scroll(0, mode="absolute")

    # Determine the type for each column in the row
    types = []
    for value in example_row:
        if isinstance(value, int):
            types.append(int)
        elif isinstance(value, float):
            types.append(float)
        else:
            types.append(str)  # Default to string for other types

    return tuple(types)


def delete_selected_row(treeview, table_name, row_id):
    # Configuration for your database
    db_config = {
        "dbname": "kugaconstruct",
        "user": "postgres",
        "password": "postgres",
        "host": "127.0.0.1",
    }
    # Connect to the database
    conn = psycopg2.connect(**db_config)
    cur = conn.cursor()
    try:
        # Perform the delete operation
        cur.execute(f"DELETE FROM {table_name} WHERE id = %s", (row_id,))
        conn.commit()
    except Exception as e:
        print("An error occurred:", e)
    finally:
        cur.close()
        conn.close()


def add_row_to_table(treeview, table_name, new_row_data, conn, cur):
    columns = ", ".join(new_row_data.keys())
    placeholders = ", ".join(["%s"] * len(new_row_data))
    values = tuple(new_row_data.values())

    try:
        cur.execute(
            f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})",
            values,
        )
        conn.commit()
        # Refresh your TreeView to show the new row
    except Exception as e:
        print("An error occurred:", e)
        conn.rollback()


def on_add_button_clicked(treeview, table_name):
    db_config = {
        "dbname": "kugaconstruct",
        "user": "postgres",
        "password": "postgres",
        "host": "127.0.0.1",
    }
    conn = psycopg2.connect(**db_config)
    cur = conn.cursor()

    # Open a new connection for the dialog
    # Get column names for the table
    columns = get_table_columns(cur, table_name)

    # Create the dialog
    dialog = Gtk.Dialog()
    dialog.set_transient_for(treeview.get_root())
    dialog.set_modal(True)
    dialog.set_title(f"Add new row to {table_name}")

    # Create a content area and grid for entries
    content_area = dialog.get_content_area()
    grid = Gtk.Grid(column_spacing=10, row_spacing=10)
    grid.set_margin_top(10)
    grid.set_margin_bottom(10)
    grid.set_margin_start(10)
    grid.set_margin_end(10)
    entries = {}

    for i, (col_name, _) in enumerate(columns):
        label = Gtk.Label(label=col_name)
        entry = Gtk.Entry()
        grid.attach(label, 0, i, 1, 1)
        grid.attach(entry, 1, i, 1, 1)
        entries[col_name] = entry

    content_area.append(grid)

    # Add buttons to the dialog
    dialog.add_action_widget(Gtk.Button(label="Cancel"), Gtk.ResponseType.CANCEL)
    dialog.add_action_widget(
        Gtk.Button(label="Add"),
        Gtk.ResponseType.OK,
    )
    dialog.present()

    # Connect the response signal
    dialog.connect(
        "response",
        on_response,
        entries,
        treeview,
        table_name,
        conn,
        cur,
    )


def on_response(dialog, response, entries, treeview, table_name, conn, cur):
    db_config = {
        "dbname": "kugaconstruct",
        "user": "postgres",
        "password": "postgres",
        "host": "127.0.0.1",
    }
    if response == Gtk.ResponseType.OK:
        new_row_data = {col: entry.get_text() for col, entry in entries.items()}
        add_row_to_table(treeview, table_name, new_row_data, conn, cur)
        # Refresh the TreeView
        refresh_treeview(treeview, table_name, db_config)
    dialog.destroy()


def on_delete_button_clicked(treeview, table_name):
    db_config = {
        "dbname": "kugaconstruct",
        "user": "postgres",
        "password": "postgres",
        "host": "127.0.0.1",
    }
    selection = treeview.get_selection()
    model, paths = selection.get_selected_rows()
    if paths:
        row_id = model[paths[0]][0]
        delete_selected_row(treeview, table_name, row_id)
        # Refresh the TreeView
        refresh_treeview(treeview, table_name, db_config)


def get_table_columns(cur, table_name):
    cur.execute(
        f"SELECT column_name, data_type FROM information_schema.columns WHERE table_name = %s",
        (table_name,),
    )
    return cur.fetchall()


def refresh_treeview(treeview, table_name, db_config):
    # Clear the current ListStore
    treeview.set_model(None)

    # Establish a new database connection
    with psycopg2.connect(**db_config) as conn:
        with conn.cursor() as cur:
            # Get the new data from the database
            cur.execute(f"SELECT * FROM {table_name}")
            column_types = get_column_types(cur)
            new_store = Gtk.ListStore(
                *[str if tp == decimal.Decimal else tp for tp in column_types]
            )

            for row in cur.fetchall():
                # Convert each value in the row to a string if it is a Decimal
                converted_row = [
                    str(value) if isinstance(value, decimal.Decimal) else value
                    for value in row
                ]
                new_store.append(converted_row)

    # Update the TreeView with the new model
    treeview.set_model(new_store)


app = DatabaseApp()
app.run(None)
