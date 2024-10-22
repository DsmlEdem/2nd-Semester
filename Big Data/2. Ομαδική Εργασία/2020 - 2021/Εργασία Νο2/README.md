## Σημείωση για την εργασία:
Στο μέρος 2ο, ζητούμενο 6, ζητείται η εκπαίδευση μοντέλου με και χωρίς caching του trainset, η εξήγηση που δώσαμε ήταν η εξής:

> Όπως παρατηρούμε, η χρήση της cache φαίνεται να καθυστερεί την εκπαίδευση. Κάτι τέτοιο σε καμία περίπτωση δεν βγάζει νόημα, αν έχουμε γίνει όλα σωστά. Το
caching μπορεί να χρησιμοποιηθεί για να τραβάμε σύνολα δεδομένων σε ένα cluster από τη memory cache. Αυτό μπορεί να φανεί χρήσιμο για την πρόσβαση σε
αρχεία που χρειάζονται επανειλημμένα όπως για παράδειγμα στο training του MLP.
Επομένως, θα περιμέναμε κάτι τέτοιο θα ελαττώσει τον χρόνο εκπαίδευσης.
Ο λόγος που στην περίπτωση μας δεν επιταχύνει την εκπαίδευση, είναι διότι
όπως μπορεί να επιβεβαιωθεί από τα logs, συγκεκριμένα στο αρχείο logs/train.txt
κατά τη διάρκεια εκπαίδευσης με caching, κάποιοι workers απέτυχαν, επομένως
κάποια tasks έπρεπε να επανεκκινηθούν από κάποιο προηγούμενο στάδιο, οπότε
κάποια tasks έγιναν παραπάνω από μια φορά.
Μπορεί αυτό το ατυχές γεγονός να καθυστέρησε λίγο την εκπαίδευση του MLP,
όμως αναδεικνύει το fault tolerance που έχει ένα framework σαν το spark, καθώς
η αποτυχία κάποιων workers είναι πολύ σύνηθες γεγονός το οποία γίνεται όλο και
πιο συχνό όσο μεγαλώνει ο αριθμός των υπολογιστικών πυρήνων στον cluster μας.

Αυτή η εξήγηση κατά την διάρκεια της εξέτασης εκτιμήθηκε πολύ ακόμα και αν δεν πετύχαμε τα επιθυμητά αποτελέσματα ( και λόγω των workers που απέτυχαν αλλά και λόγω του
ότι δεν είχαμε χρησιμοποιήσει περίπλοκο μοντέλο) διότι μπήκαμε σε μια διαδικασία να ψάξουμε στα Logs και να βρούμε την πραγματική αιτία που 
δεν πετύχαμε τα επιθυμητά αποτελέσματα. 
