import customtkinter as ctk  # Import customtkinter for the GUI
from tkinter import filedialog, messagebox, Text, Scrollbar, VERTICAL, RIGHT, Y  # Import necessary modules from tkinter
from bs4 import BeautifulSoup  # Import BeautifulSoup for web scraping
import requests  # Import requests for HTTP requests
import pandas as pd  # Import pandas for data manipulation


class WebScraperApp:
    def __init__(self, root):
        self.root = root  # Initialize the root window
        self.root.title("Table Web Scraper")  # Set the title of the window
        self.root.iconbitmap("web-crawler.ico")  # Set the icon of the window
        self.root.resizable(False, False)  # Make the window non-resizable
        self.center_window(800, 450)  # Center the window on the screen

        ctk.set_appearance_mode("dark")  # Set the appearance mode
        ctk.set_default_color_theme("blue")  # Set the color theme

        # Create the main frame
        self.frame = ctk.CTkFrame(root)
        self.frame.pack(padx=20, pady=20, fill="both", expand=True)

        # Create URL entry
        self.url_label = ctk.CTkLabel(self.frame, text="URL:")
        self.url_label.pack(pady=5)
        self.url_entry = ctk.CTkEntry(self.frame, width=600)
        self.url_entry.pack(pady=5)

        # Create Selector entry
        self.selector_label = ctk.CTkLabel(self.frame, text="CSS Selector (for table):")
        self.selector_label.pack(pady=5)
        self.selector_entry = ctk.CTkEntry(self.frame, width=600)
        self.selector_entry.pack(pady=5)

        # Create a frame for the text widget and scrollbar
        self.text_frame = ctk.CTkFrame(self.frame)
        self.text_frame.pack(padx=80, pady=(10, 10), fill="both", expand=True)

        # Create text widget for data preview
        self.data_text = Text(self.text_frame, height=10, width=80)
        self.data_text.pack(side="left", fill="both", expand=True)

        # Create and pack the scrollbar
        self.scrollbar = Scrollbar(self.text_frame, orient=VERTICAL, command=self.data_text.yview)
        self.scrollbar.pack(side=RIGHT, fill=Y)

        # Configure the text widget to use the scrollbar
        self.data_text.config(yscrollcommand=self.scrollbar.set)

        # Create a frame for the buttons
        self.button_frame = ctk.CTkFrame(self.frame)
        self.button_frame.pack(pady=(5, 10))

        # Create scrape button
        self.scrape_button = ctk.CTkButton(self.button_frame, text="Scrape", command=self.scrape_data)
        self.scrape_button.pack(side="left", padx=(0, 5))

        # Create download button
        self.download_button = ctk.CTkButton(self.button_frame, text="Download CSV", command=self.download_csv,
                                             state='disabled')
        self.download_button.pack(side="left", padx=(5, 5))

        # Create exit button
        self.exit_button = ctk.CTkButton(self.button_frame, text="Exit", command=root.quit)
        self.exit_button.pack(side="left", padx=(5, 0))

        # Initialize variables
        self.df = None

    def center_window(self, width, height):
        screen_width = self.root.winfo_screenwidth()  # Get the screen width
        screen_height = self.root.winfo_screenheight()  # Get the screen height
        x = int((screen_width / 2) - (width / 2))  # Calculate x position
        y = int((screen_height / 2) - (height / 2))  # Calculate y position
        self.root.geometry(f"{width}x{height}+{x}+{y}")  # Set the geometry of the window

    def scrape_data(self):
        url = self.url_entry.get()  # Get the URL from the entry
        selector = self.selector_entry.get()  # Get the CSS selector from the entry

        if not url or not selector:  # Check if URL or selector is empty
            messagebox.showerror("Error", "Please fill all fields")  # Show error message
            return

        try:
            page = requests.get(url)  # Send a GET request to the URL
            page.raise_for_status()  # Raise an HTTPError for bad responses (4xx and 5xx)
            soup = BeautifulSoup(page.text, 'html.parser')  # Parse the HTML content with BeautifulSoup
            table = soup.select_one(selector)  # Select the table using the CSS selector

            if not table:  # Check if the table is found
                messagebox.showerror("Error", "No table found with the given CSS selector")  # Show error message
                return

            titles = table.select('th')  # Select the headers
            titles_table = [title.text.strip() for title in titles]  # Extract the text from each header element

            self.df = pd.DataFrame(columns=titles_table)  # Create an empty DataFrame with the headers as columns

            all_data = table.select('tr')  # Select all rows in the table
            for row in all_data[1:]:
                row_data = row.select('td')
                each_row_data = [cell.text.strip() for cell in row_data]
                if each_row_data:  # To avoid appending empty rows
                    if len(each_row_data) < len(titles_table):  # Check if row data is less than titles
                        each_row_data.extend(
                            [''] * (len(titles_table) - len(each_row_data)))  # Add empty strings to match the length
                    elif len(each_row_data) > len(titles_table):  # Check if row data is more than titles
                        each_row_data = each_row_data[:len(titles_table)]  # Trim the row data to match the length
                    self.df.loc[len(self.df)] = each_row_data  # Append the row to the DataFrame

            if not self.df.empty:  # Check if the DataFrame is not empty
                self.data_text.delete(1.0, "end")  # Clear the text widget
                self.data_text.insert("end", self.df.head().to_string())  # Insert the DataFrame into the text widget
                messagebox.showinfo("Success", "Data scraped successfully")  # Show success message
                self.download_button.configure(state='normal')  # Enable the download button
            else:
                messagebox.showerror("Error", "No data found in the tables")  # Show error message

        except requests.exceptions.RequestException as e:  # Handle HTTP request exceptions
            messagebox.showerror("Error", f"HTTP Error: {e}")  # Show error message
        except Exception as e:  # Handle other exceptions
            messagebox.showerror("Error", str(e))  # Show error message

    def download_csv(self):
        if self.df is not None:  # Check if the DataFrame is not None
            file_path = filedialog.asksaveasfilename(defaultextension=".csv",
                                                     filetypes=[("CSV files", "*.csv")])  # Show save file dialog
            if file_path:  # Check if a file path is selected
                self.df.to_csv(file_path, index=False)  # Save the DataFrame to a CSV file
                messagebox.showinfo("Success", "CSV file has been saved successfully!")  # Show success message
        else:
            messagebox.showerror("Error", "No data to save")  # Show error message if no data to save


# Initialize the main application window
if __name__ == "__main__":
    root = ctk.CTk()  # Create the root window
    app = WebScraperApp(root)  # Create an instance of the WebScraperApp
    root.mainloop()  # Run the main event loop
