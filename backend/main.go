package main

import (
	"encoding/json"
	"io/ioutil"
	"log"
	"net/http"
)

type Contact struct {
	ID    int    `json:"id"`
	Name  string `json:"name"`
	Phone string `json:"phone"`
	Email string `json:"email"`
}

var contacts []Contact
var fileName = "contacts.json"

func loadContacts() {
	data, err := ioutil.ReadFile(fileName)
	if err == nil {
		json.Unmarshal(data, &contacts)
	}
}
func saveContacts() {
	data, _ := json.MarshalIndent(contacts, "", "  ")
	ioutil.WriteFile(fileName, data, 0644)
}
func getContacts(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")

	if contacts == nil {
		contacts = []Contact{}
	}

	json.NewEncoder(w).Encode(contacts)
}
func addContact(w http.ResponseWriter, r *http.Request) {
	var c Contact
	json.NewDecoder(r.Body).Decode(&c)
	c.ID = len(contacts) + 1
	contacts = append(contacts, c)
	saveContacts()
	w.WriteHeader(http.StatusCreated)
}
func deleteContact(w http.ResponseWriter, r *http.Request) {
	id := r.URL.Query().Get("id")
	var updated []Contact
	for _, c := range contacts {
		if string(rune(c.ID+'0')) != id {
			updated = append(updated, c)
		}
	}
	contacts = updated
	saveContacts()
}
func main() {
	loadContacts()

	http.HandleFunc("/contacts", getContacts)
	http.HandleFunc("/add", addContact)
	http.HandleFunc("/delete", deleteContact)

	log.Println("Go backend running on http://localhost:8080")
	http.ListenAndServe(":8080", nil)
}
