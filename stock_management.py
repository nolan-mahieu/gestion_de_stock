import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import csv
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog, messagebox
import mysql.connector
from db_config import db_config

# Fonctions pour interagir avec la base de données
def ajouter_produit(nom, description, prix, quantite, id_categorie):
    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()
        query = "INSERT INTO produit (nom, description, prix, quantite, id_categorie) VALUES (%s, %s, %s, %s, %s)"
        cursor.execute(query, (nom, description, prix, quantite, id_categorie))
        connection.commit()
        return cursor.lastrowid
    except Exception as e:
        print(e)
    finally:
        if connection:
            cursor.close()
            connection.close()

def modifier_produit(id, nom, description, prix, quantite, id_categorie):
    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()
        query = "UPDATE produit SET nom=%s, description=%s, prix=%s, quantite=%s, id_categorie=%s WHERE id=%s"
        cursor.execute(query, (nom, description, prix, quantite, id_categorie, id))
        connection.commit()
    except Exception as e:
        print(e)
    finally:
        if connection:
            cursor.close()
            connection.close()

def supprimer_produit(id):
    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()
        query = "DELETE FROM produit WHERE id=%s"
        cursor.execute(query, (id,))
        connection.commit()
    except Exception as e:
        print(e)
    finally:
        if connection:
            cursor.close()
            connection.close()

def recuperer_produits():
    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()
        query = "SELECT * FROM produit"
        cursor.execute(query)
        return cursor.fetchall()
    except Exception as e:
        print(e)
    finally:
        if connection:
            cursor.close()
            connection.close()

def recuperer_categories():
    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()
        query = "SELECT * FROM categorie"
        cursor.execute(query)
        return cursor.fetchall()
    except Exception as e:
        print(e)
    finally:
        if connection:
            cursor.close()
            connection.close()

def recuperer_produits_par_categorie(category_name):
    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()
        query = """SELECT p.id, p.nom, p.description, p.prix, p.quantite, p.id_categorie
                   FROM produit p
                   JOIN categorie c ON p.id_categorie = c.id
                   WHERE c.nom = %s"""
        cursor.execute(query, (category_name,))
        return cursor.fetchall()
    except mysql.connector.Error as error:
        print(f"Error: {error}")
    finally:
        if connection:
            cursor.close()
            connection.close()

def create_product_quantity_chart(app):
    categories = recuperer_categories()
    quantities = [sum(p[4] for p in recuperer_produits_par_categorie(c[1])) for c in categories]
    
    fig, ax = plt.subplots()
    ax.bar([c[1] for c in categories], quantities)

    ax.set_xlabel('Catégories')
    ax.set_ylabel('Quantités')
    ax.set_title('Quantité de produits par catégorie')

    return fig

# Créez l'interface graphique en utilisant tkinter
class StockManagementApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Gestion de stock")
        self.geometry("800x600")

        # Création des éléments d'interface graphique
        self.product_tree = ttk.Treeview(self, columns=("id", "nom", "description", "prix", "quantite", "id_categorie"), show="headings")
        self.product_tree.heading("id", text="ID")
        self.product_tree.heading("nom", text="Nom")
        self.product_tree.heading("description", text="Description")
        self.product_tree.heading("prix", text="Prix")
        self.product_tree.heading("quantite", text="Quantité")
        self.product_tree.heading("id_categorie", text="ID Catégorie")
        self.product_tree.pack(fill=tk.BOTH, expand=True)

        
        self.export_csv_button = tk.Button(self, text="Exporter CSV", command=self.export_csv)
        self.export_csv_button.pack(side=tk.LEFT)

        self.category_filter_label = tk.Label(self, text="Filtrer par catégorie :")
        self.category_filter_label.pack(side=tk.LEFT)

        self.category_filter_combobox = ttk.Combobox(self, values=["Toutes"] + [c[1] for c in recuperer_categories()])
        self.category_filter_combobox.pack(side=tk.LEFT)
        self.category_filter_combobox.current(0)
        self.category_filter_combobox.bind("<<ComboboxSelected>>", self.apply_category_filter)


        # Boutons pour ajouter, modifier et supprimer des produits
        self.add_product_button = tk.Button(self, text="Ajouter un produit", command=self.add_product)
        self.add_product_button.pack(side=tk.LEFT)

        self.edit_product_button = tk.Button(self, text="Modifier un produit", command=self.edit_product)
        self.edit_product_button.pack(side=tk.LEFT)

        self.delete_product_button = tk.Button(self, text="Supprimer un produit", command=self.delete_product)
        self.delete_product_button.pack(side=tk.LEFT)

        self.update_product_list()

        self.chart = create_product_quantity_chart(self)
        self.chart_canvas = FigureCanvasTkAgg(self.chart, master=self)
        self.chart_canvas.get_tk_widget().pack(side=tk.BOTTOM)

    def update_product_list(self):
        products = recuperer_produits()
        self.product_tree.delete(*self.product_tree.get_children())
        for product in products:
            self.product_tree.insert('', 'end', values=product)

    def add_product(self):
        # Ouvrir une fenêtre pour ajouter un nouveau produit
        product_form = ProductForm(self, "Ajouter un produit", ajouter_produit)
        product_form.grab_set()
        self.wait_window(product_form)
        self.update_product_list()

    def edit_product(self):
        selected_item = self.product_tree.selection()
        if selected_item:
            product_id = self.product_tree.item(selected_item)['values'][0]
            product_form = ProductForm(self, "Modifier un produit", modifier_produit, product_id)
            product_form.grab_set()
            self.wait_window(product_form)
            self.update_product_list()
        else:
            messagebox.showwarning("Sélectionnez un produit", "Veuillez sélectionner un produit à modifier.")

    def delete_product(self):
        selected_item = self.product_tree.selection()
        if selected_item:
            product_id = self.product_tree.item(selected_item)['values'][0]
            supprimer_produit(product_id)
            self.update_product_list()
        else:
            messagebox.showwarning("Sélectionnez un produit", "Veuillez sélectionner un produit à supprimer.")

    
    def apply_category_filter(self, event=None):
        category_filter = self.category_filter_combobox.get()
        if category_filter == "Toutes":
            products = recuperer_produits()
        else:
            products = recuperer_produits_par_categorie(category_filter)

        self.product_tree.delete(*self.product_tree.get_children())
        for product in products:
            self.product_tree.insert('', 'end', values=product)

        self.chart_canvas.get_tk_widget().destroy()
        self.chart = create_product_quantity_chart(self)
        self.chart_canvas = FigureCanvasTkAgg(self.chart, master=self)
        self.chart_canvas.get_tk_widget().pack(side=tk.BOTTOM)

    def export_csv(self):
        category_filter = self.category_filter_combobox.get()
        if category_filter == "Toutes":
            products = recuperer_produits()
        else:
            products = recuperer_produits_par_categorie(category_filter)

        if not products:
            messagebox.showwarning("Aucun produit à exporter", "Il n'y a aucun produit à exporter.")
            return

        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv"), ("All files", "*.*")])

        if file_path:
            with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                csv_writer = csv.writer(csvfile)
                csv_writer.writerow(["ID", "Nom", "Description", "Prix", "Quantité", "ID Catégorie"])
                for product in products:
                    csv_writer.writerow(product)

            messagebox.showinfo("Export réussi", f"Les produits ont été exportés avec succès dans le fichier {file_path}.")

class ProductForm(tk.Toplevel):
    def __init__(self, parent, title, action, product_id=None):
        super().__init__(parent)
        self.title(title)
        self.geometry("400x300")

        self.name_label = tk.Label(self, text="Nom :")
        self.name_label.pack()
        self.name_entry = tk.Entry(self)
        self.name_entry.pack()

        self.description_label = tk.Label(self, text="Description :")
        self.description_label.pack()
        self.description_entry = tk.Entry(self)
        self.description_entry.pack()

        self.price_label = tk.Label(self, text="Prix :")
        self.price_label.pack()
        self.price_entry = tk.Entry(self)
        self.price_entry.pack()

        self.quantity_label = tk.Label(self, text="Quantité :")
        self.quantity_label.pack()
        self.quantity_entry = tk.Entry(self)
        self.quantity_entry.pack()

        self.category_label = tk.Label(self, text="Catégorie :")
        self.category_label.pack()
        self.category_combobox = ttk.Combobox(self, values=[c[1] for c in recuperer_categories()])
        self.category_combobox.pack()

        self.submit_button = tk.Button(self, text="Soumettre", command=self.submit)
        self.submit_button.pack()

        self.action = action
        self.product_id = product_id

        if product_id:
            self.load_product_data()

    def load_product_data(self):
        try:
            connection = mysql.connector.connect(**db_config)
            cursor = connection.cursor()
            query = "SELECT * FROM produit WHERE id=%s"
            cursor.execute(query, (self.product_id,))
            product = cursor.fetchone()
        except Exception as e:
            print(e)
        finally:
            if connection:
                cursor.close()
                connection.close()

        if product:
            self.name_entry.insert(0, product[1])
            self.description_entry.insert(0, product[2])
            self.price_entry.insert(0, product[3])
            self.quantity_entry.insert(0, product[4])
            self.category_combobox.set(product[5])

    def submit(self):
        name = self.name_entry.get()
        description = self.description_entry.get()
        price = int(self.price_entry.get())
        quantity = int(self.quantity_entry.get())
        id_categorie = recuperer_categories()[self.category_combobox.current()][0]

        if self.product_id:
            self.action(self.product_id, name, description, price, quantity, id_categorie)
        else:
            self.action(name, description, price, quantity, id_categorie)

        self.destroy()

if __name__ == "__main__":
    app = StockManagementApp()
    app.mainloop()