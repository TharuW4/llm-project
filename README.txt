1. REQUIREMENTS

Check if the Llama model is installed:
    ollama list

If llama3.2 is missing, download it:
    ollama pull llama3.2

Check installed Python packages:
    py -m pip show langchain langchain-ollama langgraph

Install missing Python packages (only if needed):
    py -m pip install langchain langchain-ollama langgraph



2. RUN THE PROJECT

    py main.py
    Type exit to stop the program.



3. SAMPLE QUESTIONS (TYPE THESE INTO THE TERMINAL)
--------------------------------------------------

HOTEL INFORMATION - keyword-based RAG tool
1. Does your hotel have a swimming pool?
2. What time does the swimming pool close?
3. Is free Wi-Fi available?
4. Are pets allowed in the hotel?
5. What time is breakfast served?
6. Can guests smoke inside hotel rooms?

ROOMS AND PRICES - check_rooms tool
7. Show me all hotel room types and prices.
8. Which rooms are available on 2026-10-25?
9. Show available family rooms for 2026-10-25.

BOOKINGS - book_room tool
10. Book room 103 for Kasun, 2 guests, on 2026-10-25.
11. Book room 103 for Amal, 2 guests, on 2026-10-25.
12. Book room 103 for Amal, 2 guests, on 2026-10-26.
13. Book room 101 for Nimal, 3 guests, on 2026-10-25.

CANCELLATION - cancel_booking tool
14. Cancel Kasun's booking for room 103 on 2026-10-25.
15. Book room 103 for Amal, 2 guests, on 2026-10-25.

IMPORTANT: To test duplicate booking and cancellation, ask questions
10 through 15 in order during the SAME program run.

