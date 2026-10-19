from langchain.agents import create_agent
from langchain_core.messages import AIMessage, ToolMessage
from langchain_core.tools import tool
from langchain_ollama import ChatOllama


#Hotel rooms
rooms = {
    101: {"type": "Single", "capacity": 1, "price": 5000},
    102: {"type": "Single", "capacity": 1, "price": 5000},
    103: {"type": "Double", "capacity": 2, "price": 8000},
    104: {"type": "Double", "capacity": 2, "price": 8000},
    105: {"type": "Family", "capacity": 4, "price": 12000},
    106: {"type": "Family", "capacity": 4, "price": 12000},
}

#Save Bookings 
bookings = []


#Check the date format
def valid_date(date: str) -> bool:
    if len(date) != 10:
        return False
    if date[4] != "-" or date[7] != "-":
        return False
    numbers = date[:4] + date[5:7] + date[8:]
    return numbers.isdigit()

#check availability
@tool
def check_rooms(date: str = "") -> str:
    """Show hotel room types, guest capacity, prices and availability for a date (YYYY-MM-DD). Leave date empty to list rooms and prices only."""
    if date != "" and not valid_date(date):
        return "Please enter the date in YYYY-MM-DD format."

    answer = "Hotel rooms:\n"
    for room_number in rooms:
        room = rooms[room_number]
        line = f"Room {room_number}: {room['type']}, {room['capacity']} guest(s), Rs. {room['price']} per booking date"

        if date != "":
            status = "Available"
            for booking in bookings:
                if booking["room"] == room_number and booking["date"] == date:
                    status = "Booked"
            line = line + ", " + status

        answer = answer + line + "\n"

    if date == "":
        answer = answer + "Give a booking date to check availability."
    return answer


#book room
@tool
def book_room(name: str, room_number: int, guests: int, date: str) -> str:
    """Book a hotel room for one whole date (YYYY-MM-DD). Needs guest name, room number, number of guests and date."""
    name = name.strip()
    if name == "":
        return "Please provide the guest's name."
    if room_number not in rooms:
        return "This room does not exist."
    if not valid_date(date):
        return "Please enter the booking date in YYYY-MM-DD format."
    if guests < 1 or guests > rooms[room_number]["capacity"]:
        return "Invalid guest count for this room."

    for booking in bookings:
        if booking["room"] == room_number and booking["date"] == date:
            return "Room is already booked for this date. Choose another room or date."

    bookings.append({
        "name": name,
        "room": room_number,
        "guests": guests,
        "date": date,
    })
    price = rooms[room_number]["price"]
    return f"BOOKING CONFIRMED: {name}, Room {room_number}, {guests} guest(s), {date}. Price: Rs. {price}."


#cancel booking
@tool
def cancel_booking(name: str, room_number: int, date: str) -> str:
    """Cancel a booking using the guest name, room number and booking date (YYYY-MM-DD)."""
    for index, booking in enumerate(bookings):
        if (booking["name"].lower() == name.strip().lower()
                and booking["room"] == room_number
                and booking["date"] == date):
            bookings.pop(index)
            return f"BOOKING CANCELLED: Room {room_number} for {name} on {date}."
    return "No matching booking found. Check guest name, room number and date."


#keyword rag
stopwords = {
    "a", "an", "the", "is", "are", "to", "of", "on", "in", "for", "and",
    "my", "i", "do", "does", "how", "what", "if", "it", "with", "get",
    "your", "you", "or", "will", "can", "have", "has", "at", "me", "about",
}


def words_in(text: str) -> set:
    cleaned = "".join(ch if ch.isalnum() else " " for ch in text.lower())
    return {word for word in cleaned.split() if word not in stopwords}


#search informations
HOTEL_INFO = """GREEN PALACE HOTEL Information, Facilities and Policies


1. ABOUT OUR HOTEL

Green Palace Hotel provides comfortable accommodation for individuals, couples, and families. Our hotel offers three types of rooms: Single Rooms, Double Rooms, and Family Rooms. Guests can enjoy comfortable rooms, free Wi-Fi, free parking, and access to hotel facilities.


2. ROOM TYPES AND FACILITIES

Single Room
- Suitable for one guest.
- single bed.
- Air conditioning.
- bathroom.
- Free Wi-Fi.
- Television.

Double Room
- Suitable for two guests.
- One double bed.
- Air conditioning.
- Private bathroom.
- Free Wi-Fi.
- Television.

Family Room
- Suitable for up to four guests.
- Two double beds.
- Air conditioning.
- Private bathroom.
- Free Wi-Fi.
- Television.

Room prices and current availability are provided by the hotel's booking system.


3. HOTEL FACILITIES

Wi-Fi
- Free Wi-Fi is available for all hotel guests.
- Wi-Fi access details are provided at check-in.

Parking
- Free parking is available for hotel guests.
- Parking spaces are available on a first-come, first-served basis.

Swimming Pool
- The hotel has an outdoor swimming pool.
- Opening hours are 7:00 AM to 7:00 PM.


4. FOOD AND BREAKFAST

- Breakfast is served daily from 7:00 AM to 10:00 AM.
- Guests should contact reception for additional meal arrangements.


5. HOTEL RULES AND POLICIES

- Smoking is not allowed inside hotel rooms. Guests may smoke only in designated outdoor areas.
- Pets are not allowed inside the hotel.
- The number of guests must not exceed the room's maximum capacity.


6. ROOM BOOKING INFORMATION

- Guests can ask the AI assistant to check room availability for their selected date.
- Guests can book an available room by providing their name, room number, number of guests, and booking date.
- A room can only be booked if it is available for the requested date.
- A room cannot have more than one booking on the same date.
- The same room can be booked on different dates.


7. BOOKING CANCELLATION

- Guests can request booking cancellation through the AI assistant. 
- Guests must provide their room number, name used for the reservation, and booking date.
- Once a booking is successfully cancelled, the room becomes available again for that date.


8. GUEST SERVICES

- Guests can contact reception for special request and general hotel inquiries.
- Rooms are cleaned daily.



The AI assistant can provide information about hotel facilities, room types, hotel policies, and guest services.

Current room availability, room prices, reservations, and booking cancellations are managed by the hotel's booking tools.

If information is not available in the hotel guide, guests should contact hotel reception."""


#search info tool
@tool
def search_hotel_info(question: str) -> str:
    """Search hotel information for facilities, room features, food, services and policies. Do not use for live bookings or prices."""
    text = HOTEL_INFO

    # Blank lines divide the text into small sections.
    sections = text.split("\n\n")
    question_words = words_in(question)
    best_section = ""
    best_score = 0

    for section in sections:
        shared_words = question_words & words_in(section)
        score = len(shared_words)
        if score > best_score:
            best_score = score
            best_section = section

    if best_score == 0:
        return "No matching hotel information was found. Do not guess."
    return "Hotel information:\n" + best_section


llm = ChatOllama(model="llama3.2", temperature=0)

agent = create_agent(
    llm,
    [check_rooms, book_room, cancel_booking, search_hotel_info],
    system_prompt=(
        "You are the Green Palace Hotel assistant. Answer in simple English. "
        "Use check_rooms for room types, prices and availability. "
        "Use book_room for bookings and cancel_booking for cancellations. "
        "Use search_hotel_info for questions about hotel facilities, food, services and policies. "
        "Each booking is for one whole calendar date, not a night or a date range. "
        "Dates must be YYYY-MM-DD. Ask for any missing booking information. "
        "Never say a booking is confirmed or cancelled unless the tool says so. "
        "For hotel information, answer only using the retrieved tool information. "
        "If information was not found, tell the guest to contact reception."
    )
)


#run
def main():
    print("====================================")
    print("   GREEN PALACE HOTEL AI ASSISTANT")
    print("====================================")
    print("AI Assistant Ready!\n")

    history = []
    while True:
        question = input("You: ").strip()
        if question.lower() == "exit":
            break
        if question == "":
            continue

        history.append(("user", question))
        previous_messages = len(history)

        try:
            result = agent.invoke({"messages": history}, {"recursion_limit": 15})
        except Exception as e:
            print("Error:", e)
            history.pop()
            continue

        # Print answers
        print("AI:", result["messages"][-1].content, "\n")
        history = result["messages"]


if __name__ == "__main__":
    main()
