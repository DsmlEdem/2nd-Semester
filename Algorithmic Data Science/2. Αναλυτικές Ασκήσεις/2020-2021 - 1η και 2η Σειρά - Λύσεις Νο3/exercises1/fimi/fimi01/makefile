SHELL = /bin/sh
.SUFFIXES:
.SUFFIXES: .cpp .o
srcdir=./source
OBJECTS = $(srcdir)/main.o $(srcdir)/Apriori.o $(srcdir)/Trie.o $(srcdir)/Trie_hash.o
Cpp = g++
CFLAGS = -O3 -Wall
HEADS =  $(srcdir)/Apriori.hpp $(srcdir)/Trie.hpp $(srcdir)/Trie_hash.hpp

all: ./apriori decode_items

apriori: $(OBJECTS)
	$(Cpp) $(CFLAGS) $(OBJECTS) -o ./apriori

decode_items: recode_reformat/source/main_decode.o
	$(Cpp) recode_reformat/source/main_decode.o -o recode_reformat/decode_items

$(OBJECTS): $(HEADS)
.cpp.o:
	$(Cpp) -I$(srcdir) -c $(CFLAGS) $< -o $@

clean :
	rm -f $(OBJECTS) ./apriori recode_reformat/source/main_decode.o recode_reformat/decode_items

	
