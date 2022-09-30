/***************************************************************************
                          main.cpp  -  description
                             -------------------
    begin                : Sun Dec 29 13:21:42 CET 2002
    copyright            : (C) 2002 by Ferenc Bodon
    email                : bodon@mit.bme.hu
 ***************************************************************************/

//!  This program decodes the items.
/*!
  The APRIORI algorithm implemented by the author accepts that kind of basket files where the items are positive whole numbers.
  So to mine association rules first we have to code the item, run APRIORI, and then decode the items in the output of the algorithm.
  The decoder program presumes, that the output of the APRIORI isfrom the standard input.
  The item and their code are found in a file. Each line belongs to an item.
  First the code is given, then a colon, and then the item (like 134:beer).
  The file does not have to be ordered by codes.

*/

#ifdef HAVE_CONFIG_H
#include <config.h>
#endif

#include <iostream>
#include <string>
#include <cstdlib>
#include <cstdio>
#include <fstream>
#include <map>
using namespace std;

typedef unsigned long itemtype;
//! codearray[i] stores the item belongs to code i
map<itemtype,string> codearray;

/**  It fills up the codearray.
  *
  * \param code_file_name The file that contains the items and their codes.
  */
void code_file_process( char* code_file_name )
{
   itemtype item_code;
   string   tempkar;

   ifstream kodfile(code_file_name);
   if( !kodfile )
   {
      cerr<<endl<<"Codefile does not exists."<<endl;
      exit(1);
   }
   while( kodfile )
   {
      kodfile>>item_code;
      kodfile.get();                  //reading in the colon
      getline(kodfile,tempkar);
      codearray[item_code]=tempkar;
   }
}
/**  Writes the item to the standard output.
  *
  * If no item belong to the code then the code is written.
  * \param item The code of the item.
  */
void write_decoded_item( itemtype item )
{
   if( codearray[item] != "" ) cout << codearray[item];
   else cout<<item;
}
///  Decodes the standard input and write the result to the standard output.
void decode()
{
   double         conf;
   itemtype      itemset_size=0,
                 item_index;
   unsigned long temp_stor;

   scanf("Frequent 0-itemsets:\n"); printf("Frequent 1-itemsets:\n");
   scanf("itemset (occurrence)\n"); cout<<"itemset (occurrence)"<<endl;
   scanf("{} (%lu)\n",&temp_stor); cout<<"{} ("<<temp_stor<<')'<<endl;

   while( scanf("Frequent %lu-itemsets:\n",&itemset_size) == 1 )
   {
      printf("Frequent %lu-itemsets:\n",itemset_size);
      scanf("itemset (occurrence)\n");cout<<"itemset (occurrence)"<<endl;
      while( scanf("%lu ",&temp_stor) == 1 )
      {
         write_decoded_item(temp_stor);
         cout<<' ';
         for( item_index = 1; item_index < itemset_size; item_index++)
         {
            scanf("%lu ", &temp_stor);
            write_decoded_item( temp_stor );
            cout<<' ';
         }
         scanf("(%lu)\n",&temp_stor);
         cout<< '(' << temp_stor << ')' << endl;
      }
   }

   scanf("\nAssociation rules:\ncondition ==> consequence (confidence, occurrence)\n");
   cout<<endl<<"\nAssociation rules:\ncondition ==> consequence (confidence, occurrence)"<<endl;
   while( scanf("%lu ",&temp_stor) == 1 )
   {
      write_decoded_item(temp_stor);
      cout<<' ';
   }
   scanf("==>"); cout<<"==>";
   while( scanf(" %lu",&temp_stor) == 1 )
   {
      cout<<' ';
      write_decoded_item(temp_stor);
   }
   scanf(" (%lf, %lu)\n", &conf, &temp_stor); cout<<" ("<<conf<<", "<<temp_stor<<')'<<endl;
}

int main( int argc, char *argv[] )
{
   if (argc<2)
   {
      cout << endl << "Please specify the code table file as argument!" <<endl;
      exit(2);
   }
   code_file_process(argv[1]);
   decode();
   return 0;
}
