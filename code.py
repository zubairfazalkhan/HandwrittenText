import pandas as pd
from PIL import Image, ImageDraw, ImageFont
import os
import random
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import landscape

# Function to list available fonts and get user selection
def choose_font(directory):
    available_fonts = [f for f in os.listdir(directory) if f.endswith('.ttf')]
    if len(available_fonts) == 0:
        raise ValueError("No font files found in the directory.")
    
    print("Available fonts:")
    for i, font in enumerate(available_fonts):
        print(f"{i + 1}. {font}")
    
    while True:
        try:
            choice = int(input(f"Choose a font (enter the number): "))
            if 1 <= choice <= len(available_fonts):
                return os.path.join(directory, available_fonts[choice - 1])
            else:
                print(f"Invalid choice. Please enter a number between 1 and {len(available_fonts)}.")
        except ValueError:
            print("Invalid input. Please enter a number.")

# Define your paths
EXCEL_FILE = 'motivated seller list.xlsx'  # Path to the uploaded Excel file
SAVE_DIR = 'handwritten_texts'
FONTS_DIR = 'fonts'  # Directory containing font files
PDF_FILE = os.path.join(SAVE_DIR, 'handwritten_texts.pdf')  # Path to save the PDF

# Create save directory if it doesn't exist
os.makedirs(SAVE_DIR, exist_ok=True)

# Get font path from user
FONT_PATH = choose_font(FONTS_DIR)

# Read Excel file
df = pd.read_excel(EXCEL_FILE)

# Get the complete address from the user as a single input
# user_full_address = input("Enter the complete address for the top left (e.g., 'John Doe, 1234 Elm St, Springfield, IL 62704'): ")
user_full_address = "Morgan Iacolucci, 1653 21st Ave, Seattle, WA 98122"

# Split the user input into lines for placement on the image
user_address_lines = user_full_address.split(', ')
user_address_text = f"{'Morgan Iacolucci'}\n{'1653 21st ave'}\n{'Seattle'}, {'WA'} {'98122'}"
#user_address_text = "\n".join(user_address_lines)

img_width, img_height = 2031, 864 

# Function to draw text on an image
def draw_text(text, user_text, file_name, font_path):
    # Load a font
    font_size = 70
    font = ImageFont.truetype(font_path, font_size)  # Increased font size for better readability
    
    # Create a white background image
    # img_width, img_height = 677, 288 #2000, 1500  # Define the size of the image
    img = Image.new('RGB', (img_width, img_height), color = (255, 255, 255))
    d = ImageDraw.Draw(img)

    # Split text into lines
    lines = text.split('\n')
    user_lines = user_text.split('\n')
    
    
    # Calculate the middle position for the main address
    max_line_width = 0
    total_height = 0
    
    for line in lines:
        text_bbox = d.textbbox((0, 0), line, font=font)
        line_width = text_bbox[2] - text_bbox[0]
        line_height = text_bbox[3] - text_bbox[1]
        max_line_width = max(max_line_width, line_width)
        total_height += line_height + 10  # Adding line spacing

    x_start = (img_width - max_line_width) // 2
    y_start = ((img_height - total_height) // 2)*1.2

    # Draw the main address in the center
    x, y = x_start, y_start
    text_color = (0, 0, 139)  # Dark blue color for the text (R, G, B values)
    
    for line in lines:
        d.text((x, y), line, font=font, fill=text_color)
        line_height = d.textbbox((0, 0), line, font=font)[3] - d.textbbox((0, 0), line, font=font)[1]
        y += line_height + 10

    # Draw the user-provided address in the top left corner
    max_user_line_width = 0
    user_total_height = 0

    for line in user_lines:
        text_bbox = d.textbbox((0, 0), line, font=font)
        line_width = text_bbox[2] - text_bbox[0]
        line_height = text_bbox[3] - text_bbox[1]
        max_user_line_width = max(max_user_line_width, line_width)
        user_total_height += line_height + 10  # Adding line spacing
    
    x_user_start = 50  # Start close to the left edge
    y_user_start = 50  # Start close to the top edge

    x, y = x_user_start, y_user_start
    for line in user_lines:
        d.text((x, y), line, font=font, fill=text_color)
        line_height = d.textbbox((0, 0), line, font=font)[3] - d.textbbox((0, 0), line, font=font)[1]
        y += line_height + 10

    # Save the image
    img.save(os.path.join(SAVE_DIR, f'{file_name}.jpeg'), 'JPEG')

# Loop through each row in the DataFrame
for index, row in df.iterrows():
    addressee = row['Adressee']
    address = row['Address']
    city = row['City']
    state = row['State']
    zip_code = row['Zip']
    text = f"{addressee}\n{address}\n{city}, {state} {zip_code}"
    file_name = f'document_{index + 1}'
    draw_text(text, user_address_text, file_name, FONT_PATH)

print('Handwritten images have been saved.')

# Define new page size
# PAGE_WIDTH, PAGE_HEIGHT = 676.8, 288  # 9.4 inches * 4 inches in points
PAGE_WIDTH, PAGE_HEIGHT = img_width/3, img_height/3

# Create a PDF with all the images
c = canvas.Canvas(PDF_FILE, pagesize=(PAGE_WIDTH, PAGE_HEIGHT))

for index in range(len(df)):
    img_path = os.path.join(SAVE_DIR, f'document_{index + 1}.jpeg')
    # Open the image to get its dimensions
    img = Image.open(img_path)
    
    # Calculate scaling to fit the image within the PDF page
    img_width, img_height = img.size
    #scaling_factor = min(PAGE_WIDTH / img_width, PAGE_HEIGHT / img_height)
    scaling_factor = 3
    new_width = img_width / scaling_factor
    new_height = img_height / scaling_factor
    
    # Calculate positions to center the image
    x = (PAGE_WIDTH - new_width) / 2
    y = (PAGE_HEIGHT - new_height) / 2
    
    # Draw the image on the PDF
    c.drawImage(img_path, x, y, new_width, new_height)
    c.showPage()

c.save()
print('PDF with handwritten images has been saved.')
