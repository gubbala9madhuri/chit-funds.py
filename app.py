import streamlit as st
import sqlite3
import random

# Connect to the SQLite database
conn = sqlite3.connect('chit_funds.db')
cursor = conn.cursor()

# Create tables if they don't exist
cursor.execute("""
CREATE TABLE IF NOT EXISTS members (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    contribution REAL,
    loan_received REAL
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS bids (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    member_id INTEGER,
    bid_amount REAL,
    winner BOOLEAN,
    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (member_id) REFERENCES members (id)
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS penalties (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    member_id INTEGER,
    penalty_amount REAL,
    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (member_id) REFERENCES members (id)
)
""")
conn.commit()

# Admin Page Title
st.title("Admin Dashboard for Chit Funds")

# Sidebar Navigation
menu = ["Home", "Add Member", "View Members", "Update Contribution", "Update Loan", "Remove Member", "Place Bid", "View Bids", "Bid Winner", "Add Penalty", "View Penalties", "View Member Loan History"]
choice = st.sidebar.selectbox("Select an option", menu)

# --- Add Member ---
if choice == "Add Member":
    st.subheader("Add New Member")
    member_name = st.text_input("Enter member's name")
    initial_contribution = st.number_input("Enter initial contribution", min_value=0.0)
    initial_loan = st.number_input("Enter initial loan amount", min_value=0.0)

    if st.button("Add Member"):
        if member_name != "":
            cursor.execute("INSERT INTO members (name, contribution, loan_received) VALUES (?, ?, ?)",
                           (member_name, initial_contribution, initial_loan))
            conn.commit()
            st.success(f"Member {member_name} added successfully!")
        else:
            st.error("Please enter a valid name.")

# --- View Members ---
elif choice == "View Members":
    st.subheader("View All Members")
    cursor.execute("SELECT * FROM members")
    members = cursor.fetchall()

    if members:
        for member in members:
            st.write(f"ID: {member[0]}, Name: {member[1]}, Contribution: {member[2]}, Loan Received: {member[3]}")
    else:
        st.write("No members found.")

# --- Update Contribution ---
elif choice == "Update Contribution":
    st.subheader("Update Member Contribution")
    cursor.execute("SELECT id, name FROM members")
    members = cursor.fetchall()

    member_ids = [f"{member[0]} - {member[1]}" for member in members]
    member_to_update = st.selectbox("Select a member", member_ids)
    member_id = int(member_to_update.split(" ")[0])

    new_contribution = st.number_input("Enter new contribution amount", min_value=0.0)

    if st.button("Update Contribution"):
        if new_contribution >= 0:
            cursor.execute("UPDATE members SET contribution = ? WHERE id = ?", (new_contribution, member_id))
            conn.commit()
            st.success("Contribution updated successfully!")
        else:
            st.error("Contribution cannot be negative.")

# --- Update Loan ---
elif choice == "Update Loan":
    st.subheader("Update Member Loan")
    cursor.execute("SELECT id, name FROM members")
    members = cursor.fetchall()

    member_ids = [f"{member[0]} - {member[1]}" for member in members]
    member_to_update = st.selectbox("Select a member", member_ids)
    member_id = int(member_to_update.split(" ")[0])

    new_loan = st.number_input("Enter new loan amount", min_value=0.0)

    if st.button("Update Loan"):
        if new_loan >= 0:
            cursor.execute("UPDATE members SET loan_received = ? WHERE id = ?", (new_loan, member_id))
            conn.commit()
            st.success("Loan updated successfully!")
        else:
            st.error("Loan amount cannot be negative.")

# --- Remove Member ---
elif choice == "Remove Member":
    st.subheader("Remove Member")
    cursor.execute("SELECT id, name FROM members")
    members = cursor.fetchall()

    member_ids = [f"{member[0]} - {member[1]}" for member in members]
    member_to_remove = st.selectbox("Select a member to remove", member_ids)
    member_id = int(member_to_remove.split(" ")[0])

    if st.button("Remove Member"):
        cursor.execute("DELETE FROM members WHERE id = ?", (member_id,))
        conn.commit()
        st.success("Member removed successfully!")

# --- Place Bid ---
elif choice == "Place Bid":
    st.subheader("Place a Bid")
    cursor.execute("SELECT id, name FROM members")
    members = cursor.fetchall()

    member_ids = [f"{member[0]} - {member[1]}" for member in members]
    member_to_bid = st.selectbox("Select a member to place a bid", member_ids)
    member_id = int(member_to_bid.split(" ")[0])

    bid_amount = st.number_input("Enter bid amount", min_value=0.0)

    if st.button("Place Bid"):
        if bid_amount > 0:
            cursor.execute("INSERT INTO bids (member_id, bid_amount, winner) VALUES (?, ?, ?)",
                           (member_id, bid_amount, False))
            conn.commit()
            st.success(f"Bid of amount {bid_amount} placed by {member_to_bid}!")
        else:
            st.error("Bid amount must be greater than 0.")

# --- View Bids ---
elif choice == "View Bids":
    st.subheader("View All Bids")
    cursor.execute("SELECT b.id, m.name, b.bid_amount, b.date FROM bids b JOIN members m ON b.member_id = m.id")
    bids = cursor.fetchall()

    if bids:
        for bid in bids:
            st.write(f"Bid ID: {bid[0]}, Member: {bid[1]}, Bid Amount: {bid[2]}, Date: {bid[3]}")
    else:
        st.write("No bids placed yet.")

# --- Bid Winner ---
elif choice == "Bid Winner":
    st.subheader("Declare Bid Winner")
    cursor.execute("SELECT b.id, m.name, b.bid_amount FROM bids b JOIN members m ON b.member_id = m.id WHERE b.winner = 0")
    bids = cursor.fetchall()

    if bids:
        bid_ids = [f"Bid ID: {bid[0]} - {bid[1]} - {bid[2]}" for bid in bids]
        bid_to_choose = st.selectbox("Select a bid to declare a winner", bid_ids)
        bid_id = int(bid_to_choose.split(" ")[2])

        if st.button("Declare Winner"):
            cursor.execute("UPDATE bids SET winner = 1 WHERE id = ?", (bid_id,))
            conn.commit()
            st.success("Bid winner declared successfully!")
    else:
        st.write("No bids available for winner declaration.")

# --- Add Penalty ---
elif choice == "Add Penalty":
    st.subheader("Add Penalty for Late Payment")
    cursor.execute("SELECT id, name FROM members")
    members = cursor.fetchall()

    member_ids = [f"{member[0]} - {member[1]}" for member in members]
    member_to_penalize = st.selectbox("Select a member to penalize", member_ids)
    member_id = int(member_to_penalize.split(" ")[0])

    penalty_amount = st.number_input("Enter penalty amount", min_value=0.0)

    if st.button("Add Penalty"):
        if penalty_amount > 0:
            cursor.execute("INSERT INTO penalties (member_id, penalty_amount) VALUES (?, ?)",
                           (member_id, penalty_amount))
            conn.commit()
            st.success(f"Penalty of {penalty_amount} added for {member_to_penalize}!")
        else:
            st.error("Penalty amount must be greater than 0.")

# --- View Penalties ---
elif choice == "View Penalties":
    st.subheader("View All Penalties")
    cursor.execute("SELECT p.id, m.name, p.penalty_amount, p.date FROM penalties p JOIN members m ON p.member_id = m.id")
    penalties = cursor.fetchall()

    if penalties:
        for penalty in penalties:
            st.write(f"Penalty ID: {penalty[0]}, Member: {penalty[1]}, Penalty Amount: {penalty[2]}, Date: {penalty[3]}")
    else:
        st.write("No penalties added yet.")

# --- View Member Loan History ---
elif choice == "View Member Loan History":
    st.subheader("View Loan History for Members")
    cursor.execute("SELECT id, name FROM members")
    members = cursor.fetchall()

    member_ids = [f"{member[0]} - {member[1]}" for member in members]
    member_to_view = st.selectbox("Select a member to view loan history", member_ids)
    member_id = int(member_to_view.split(" ")[0])

    cursor.execute("SELECT loan_received FROM members WHERE id = ?", (member_id,))
    loan_history = cursor.fetchone()

    if loan_history:
        st.write(f"Total loan received by {member_to_view}: {loan_history[0]}")
    else:
        st.write(f"No loan history found for {member_to_view}.")