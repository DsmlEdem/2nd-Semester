/***************************************************************************
                          apriori.cpp  -  description
                             -------------------
    begin                : cs dec 26 2002
    copyright            : (C) 2002 by Ferenc Bodon
    email                : bodon@mit.bme.hu
 ***************************************************************************/

#include "Apriori.hpp"
#include <iostream>
#include <vector>
#include <set>
#include <cmath>   //because of the ceil function

using namespace std;

void Apriori::read_in_a_line( FILE* filepoint )
{
   set<itemtype> tempbasket;
   char          c;
   itemtype      pos;

   basket.clear();
   do
   {
      int item = 0;
      pos = 0;
      c = getc( filepoint );
      while((c >= '0') && (c <= '9'))
      {
         item *= 10;
         item += int(c)-int('0');
         c = getc( filepoint );
         pos++;
      }
      if( pos ) tempbasket.insert( (itemtype) item );
   } while( c != '\n' && !feof(filepoint) );
   basket.resize( tempbasket.size() );
   pos = 0;
   for( set<itemtype>::iterator it = tempbasket.begin(); it != tempbasket.end(); it++, pos++)
      basket[pos] = *it;
}

void Apriori::support( FILE* basket_file, const itemtype& candidate_size )
{
   if(candidate_size == 1)
   {
      basket_number = 0;
      while( !feof(basket_file) )
      {
         read_in_a_line( basket_file );
         if( !basket.empty() )
         {
            basket_number++;
            trie->find_candidate( basket, candidate_size );
         }
      }
   }
   else if( store_input )
   {
      if (candidate_size == 2)
      {
         while( !feof(basket_file) )
         {
            read_in_a_line( basket_file );
            trie->basket_recode( basket );
            if (basket.size()>1) reduced_baskets[basket]++;
         }
      }
      for (map<vector<itemtype>,unsigned long, itemsetLess>::iterator it=reduced_baskets.begin();it!=reduced_baskets.end();it++)
         trie->find_candidate(it->first,candidate_size,it->second);
   }
   else while (!feof(basket_file))
   {
      read_in_a_line(basket_file);
      trie->basket_recode(basket);
          trie->find_candidate(basket,candidate_size);
   }
}
Apriori::Apriori(const bool& store_input, const int& trie_type,const int& child_threshold)
{
  this->store_input=store_input;
  if (trie_type==1) trie=new Trie();
  else trie=new Trie_hash(child_threshold);
  basket_number=0;
}

/**
  \param outcomefile The file the output will be written to.
  \param basket_filename The name of the datafile that contains the transactions.
  \param min_supp The relative support threshold
  \param min_conf The confidence threshold for association rules. If min_conf=0 no association rules will be extraced.
*/
void Apriori::APRIORI_alg(ofstream& outcomefile,const char* basket_filename, const double& min_supp, const double& min_conf)
{
   FILE* basket_file;
   basket_file=fopen(basket_filename,"r");
   if (basket_file==NULL) {cerr<<endl<<"File I/O error: basketfile cannot be read!"<<endl;exit(1);}

   cout<<endl<<"\t\tFinding frequent itemsets..."<<endl<<endl;
   cout<<"Number of frequent 0-itemsets is "<<trie->node_number()<<endl;   //it should be 1 :))
   itemtype candidate_size=1;
   unsigned long trie_size,trie_size_after_delete=1;
   cout<<endl<<"Determining the support of the "<<candidate_size<<"-itemset candidates!"<<endl;
   support(basket_file,candidate_size);
//   cout<<"\nBasket number"<<basket_number;
//   trie.statistics();
//   trie->show_content();
//   getchar();
   unsigned long min_supp_abs=(unsigned long) ceil(min_supp*basket_number);
   cout<<"Deleting infrequent items!"<<endl;
    trie->delete_infrequent(min_supp_abs);
   cout<<"Number of frequent "<<candidate_size<<"-itemsets is "<<trie->node_number()-trie_size_after_delete<<endl;
   trie_size_after_delete=trie->node_number();
   trie->statistics();
//   trie->show_content();
//   getchar();
   trie_size=trie->node_number();
   cout<<endl<<"Genarating "<<candidate_size+1<<"-itemset candidates!"<<endl;
   trie->candidate_generation(candidate_size);
   trie->statistics();
//   trie->show_content();
//   getchar();
   while (trie_size<trie->node_number())
   {
      candidate_size++;
      fclose(basket_file);
       basket_file=fopen(basket_filename,"r");
         cout<<"Determining the support of the "<<candidate_size<<"-itemset candidates!"<<endl;
      support(basket_file,candidate_size);
//      trie->show_content();
//      getchar();
      cout<<"Deleting infrequent itemsets!"<<endl;
         trie->delete_infrequent(min_supp_abs);
      cout<<"Number of frequent "<<candidate_size<<"-itemsets is "<<trie->node_number()-trie_size_after_delete<<endl;
      trie_size_after_delete=trie->node_number();
//      trie->show_content();
//      getchar();
      trie_size=trie->node_number();
      trie->statistics();
      cout<<endl<<"Genarating "<<candidate_size+1<<"-itemset candidates!"<<endl;
      trie->candidate_generation(candidate_size);
      trie->statistics();
//      trie->show_content();
//      getchar();
   }
   fclose(basket_file);
   trie->write_content_to_file(outcomefile);
   if (min_conf)
   {
        cout<<"\nGenerating association rules...!\n";
      trie->association(outcomefile,min_conf);
   }
     cout<<"\nMining is done!\n";
}

