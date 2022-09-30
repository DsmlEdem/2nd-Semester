/***************************************************************************
                          Trie.cpp  -  description
                             -------------------
    begin                : cs dec 26 2002
    copyright            : (C) 2002 by Ferenc Bodon
    email                : bodon@mit.bme.hu
 ***************************************************************************/


#include "Trie.hpp"
#include <cstdlib>
#include <algorithm>

/**
  \param stateIndex the state whose max_path value has to be set.
  \return true, if no update was required (original value was correct), otherwise false.
*/

void Trie::max_path_set( const unsigned long stateIndex )
{
   itemtype temp_max_path = 0;
   for(  vector<unsigned long>::iterator it_state = statearray[stateIndex].begin(); it_state != statearray[stateIndex].end(); it_state++ )
      if( temp_max_path<maxpath[*it_state]+1) temp_max_path=maxpath[*it_state]+1;
   if(  maxpath[stateIndex] != temp_max_path )
   {
      maxpath[stateIndex] = temp_max_path;
      if(  stateIndex ) max_path_set(parent[stateIndex]);
   }
}

/**
   \param fromState the state from the edge starts.
   \param toState the state to the edge points.
*/

void Trie::delete_edge( const unsigned long fromState, const unsigned long toState )
{
   vector<unsigned long>::iterator it_state = lower_bound( statearray[fromState].begin(), statearray[fromState].end(), toState );
   // we are sure, that there is an element, so if( it_state!=statearray[fromState].end() && *it_state==toState) is omitted
   itemarray[fromState].erase( it_state - statearray[fromState].begin() + itemarray[fromState].begin() );
   statearray[fromState].erase( it_state );
   if(  itemarray[fromState].empty() )
   {
      maxpath[fromState] = 0;
      max_path_set(parent[fromState]);
   }
}

/**
  \param fromState The state number that point to the new state.
  \param item The label of the new edge
  \param counter The initial counter of the new state
 */
void Trie::add_empty_state( const unsigned long fromState,itemtype item, const unsigned long counter )
{
   itemarray[fromState].push_back(item);
   statearray[fromState].push_back(itemarray.size());

   itemarray.resize(itemarray.size()+1);
   statearray.resize(itemarray.size());
   parent.push_back(fromState);
   countervector.push_back(counter);
   maxpath.push_back(0);
}

/**
  \param an_itemset The given itemset.
  \return 0, if the itemset is not included, otherwise the state number, that represents the itemset.
*/

unsigned long Trie::is_included( const set<itemtype>& an_itemset ) const
{
   unsigned long                      stateIndex=0;
   vector<itemtype>::const_iterator   it_itemvector;

   for(  set<itemtype>::const_iterator item_it = an_itemset.begin(); item_it != an_itemset.end(); item_it++ )
   {
      it_itemvector = lower_bound(itemarray[stateIndex].begin(), itemarray[stateIndex].end(), *item_it);
      if( it_itemvector != itemarray[stateIndex].end() && *it_itemvector == *item_it)
         stateIndex = statearray[stateIndex][it_itemvector-itemarray[stateIndex].begin()];
      else return 0;
   }
   return stateIndex;
}

/**
  \param maybe_candidate The itemset that has to be checked.
 */

bool Trie::is_all_subset_frequent( const set<itemtype>& maybe_candidate ) const
{
   if( maybe_candidate.size() < 3) return true;   // because of the candidate generation method!
   else
   {
      set<itemtype>                 temp_itemset(maybe_candidate);
      set<itemtype>::const_iterator item_it = --(--maybe_candidate.end());
      do
      {
         item_it--;
         temp_itemset.erase( *item_it );
         if( !is_included( temp_itemset ) ) return false;
         temp_itemset.insert( *item_it );
      }
      while ( item_it != maybe_candidate.begin() );
      return true;
   }
}

void Trie::candidate_generation_two()
{
   if(  !itemarray[0].empty() )
   {
      maxpath[0] = 2;
      temp_counter_array.reserve(itemarray[0].size()-1);
      temp_counter_array.resize(itemarray[0].size()-1);
      for( itemtype stateIndex = 0; stateIndex < itemarray[0].size()-1; stateIndex++ )
      {
         temp_counter_array[stateIndex].reserve(itemarray[0].size()-1-stateIndex );
         temp_counter_array[stateIndex].resize(itemarray[0].size()-1-stateIndex, 0);
      }
   }
}

void Trie::candidate_generation_assist( unsigned long actual_state, const itemtype frequent_size,
                                        const itemtype actual_size, set<itemtype>& maybe_candidate)
{
   itemtype edgeIndex;
   if( actual_size == frequent_size)
   {
      itemtype edgeIndex2;
      unsigned long toExtend;
      for( edgeIndex = 0; edgeIndex < itemarray[actual_state].size(); edgeIndex++ )
      {
         maybe_candidate.insert(itemarray[actual_state][edgeIndex]);
         toExtend = statearray[actual_state][edgeIndex];
         for( edgeIndex2 = edgeIndex+1; edgeIndex2 < itemarray[actual_state].size(); edgeIndex2++ )
         {
            maybe_candidate.insert(itemarray[actual_state][edgeIndex2]);
            if(  is_all_subset_frequent(maybe_candidate) )
	       add_empty_state(toExtend,itemarray[actual_state][edgeIndex2]);
            maybe_candidate.erase(itemarray[actual_state][edgeIndex2]);
         }
         if( !itemarray[toExtend].empty()) maxpath[toExtend] = 1;
         vector<itemtype>((const vector<itemtype>) itemarray[toExtend]).swap(itemarray[toExtend]);         // we know that state toExtend will not have any more children!
         vector<unsigned long>((const vector<unsigned long>) statearray[toExtend]).swap(statearray[toExtend]);  // we know that state toExtend will not have any more children!
         maybe_candidate.erase(itemarray[actual_state][edgeIndex]);
      }
      max_path_set(actual_state);
   }
   else
   {
      for( edgeIndex = 0; edgeIndex < itemarray[actual_state].size(); edgeIndex++ )
      {
         maybe_candidate.insert(itemarray[actual_state][edgeIndex]);
         candidate_generation_assist( statearray[actual_state][edgeIndex], frequent_size, actual_size+1, maybe_candidate );
         maybe_candidate.erase(itemarray[actual_state][edgeIndex]);
      }
   }
}

/**
   \param basket the given basket
   */

void Trie::find_candidate_one( const vector<itemtype>& basket )
{
  countervector[0]++;
  for( vector<itemtype>::const_iterator it_basket = basket.begin(); it_basket != basket.end(); it_basket++ )
  {
    if( *it_basket+1 >= countervector.size() ) countervector.resize( *it_basket+2, 0 );
    countervector[*it_basket+1]++;
  }
}

/**
     \param basket the given basket
     \param counter The number the processed basket occures in the transactional database
   */

void Trie::find_candidate_two( const vector<itemtype>& basket, const unsigned long counter )
{
   vector<itemtype>::const_iterator it1_basket,
                                    it2_basket;

   for( it1_basket = basket.begin(); it1_basket != basket.end()-1; it1_basket++)
      for( it2_basket = it1_basket+1; it2_basket != basket.end(); it2_basket++)
         temp_counter_array[*it1_basket-1][*it2_basket-*it1_basket-1] += counter;
}

/**
  \param basket the given basket
  \param candidate_size The size of the candidates
  \param it_basket *it_basket lead to the actual_state. Only items following this item need to be considered
  \param actual_state The index of the actual state
  \param actual_size The number of items that are already found
  \param counter The number the processed basket occures in the transactional database
*/
void Trie::find_candidate_more( const vector<itemtype>& basket, const itemtype candidate_size,
                                vector<itemtype>::const_iterator it_basket, const unsigned long actual_state,
                                const itemtype actual_size, const unsigned long counter)
{
   if( candidate_size == actual_size)
      countervector[actual_state] += counter;
   else
   {
      vector<itemtype>::iterator it_item = itemarray[actual_state].begin();
      vector<unsigned long>::iterator it_state = statearray[actual_state].begin();
      while( it_item < itemarray[actual_state].end() && candidate_size < basket.end()-it_basket+actual_size+1)
      {
         if( *it_item < *it_basket) {it_item++; it_state++;}
         else if( *it_item > *it_basket) it_basket++;
         else
         {
            if( maxpath[*it_state]+actual_size+1 == candidate_size )
               find_candidate_more( basket, candidate_size, it_basket+1, *it_state, actual_size+1, counter);
            it_item++;
            it_state++;
            it_basket++;
         }
      }
   }
}

/**
  \param min_occurrence The occurence threshold
*/

void Trie::delete_infrequent_one( const unsigned long min_occurrence )
{
   itemtype edgeIndex;

   inv_orderarray.reserve( countervector.size() );
   inv_orderarray.resize( countervector.size(), 0 );
   orderarray.resize(1);
   vector<unsigned long> temp_countervector(1);
   vector<unsigned long>::iterator it_item;

   for( edgeIndex = 1; edgeIndex < countervector.size(); edgeIndex++)
      if( countervector[edgeIndex] >= min_occurrence )
      {
         it_item = lower_bound( temp_countervector.begin()+1, temp_countervector.end(), countervector[edgeIndex]);
         orderarray.insert(orderarray.begin()+(it_item-temp_countervector.begin()), edgeIndex);
         temp_countervector.insert(it_item, countervector[edgeIndex]);
      }
   if( orderarray.size() > 1 ) maxpath[0] = 1;
   vector<itemtype>(orderarray).swap(orderarray);
   countervector.resize(1);
   for( edgeIndex = 1; edgeIndex < orderarray.size(); edgeIndex++ )
      add_empty_state( 0, edgeIndex, temp_countervector[edgeIndex] );
   for( edgeIndex = 1; edgeIndex < orderarray.size(); edgeIndex++)
      inv_orderarray[orderarray[edgeIndex]] = edgeIndex;
}

/**
  \param min_occurrence The occurence threshold
*/
void Trie::delete_infrequent_two( const unsigned long min_occurrence )
{
   itemtype stateIndex_1,
            stateIndex_2;
   for( stateIndex_1 = 1; stateIndex_1 < itemarray[0].size(); stateIndex_1++ )
   {
      for( stateIndex_2 = 0; stateIndex_2 < itemarray[0].size()-stateIndex_1; stateIndex_2++ )
        if( temp_counter_array[stateIndex_1-1][stateIndex_2] >= min_occurrence )
           add_empty_state( stateIndex_1, stateIndex_1+stateIndex_2+1, temp_counter_array[stateIndex_1-1][stateIndex_2] );
      if( !itemarray[stateIndex_1].empty() ) maxpath[stateIndex_1] = 1;
      temp_counter_array[stateIndex_1-1].clear();
      vector<unsigned long>().swap(temp_counter_array[stateIndex_1-1]);   /// temp_counter_array[stateIndex_1-1] will never be used again!
   }
   temp_counter_array.clear();
   vector< vector<unsigned long> >().swap(temp_counter_array);            /// temp_counter_array will never be used again!

   if( itemarray.size() == itemarray[0].size()+1 ) maxpath[0] = 1;
}

/**
  \param min_occurrence The occurence threshold
*/
void Trie::delete_infrequent_more( const unsigned long min_occurrence )
{
   unsigned long stateIndex=1,
                 stateIndex2,
                 os;

   for( stateIndex2 = 1; stateIndex2 < itemarray.size(); stateIndex2++)
   {
      os = parent[stateIndex2];
      if( countervector[stateIndex2] >= min_occurrence )
      {
         if( stateIndex != stateIndex2 )
         {
            vector<unsigned long>::iterator it_state = lower_bound( statearray[os].begin(), statearray[os].end(), stateIndex2 );
            *it_state = stateIndex;
            itemarray[stateIndex] = itemarray[stateIndex2];
            statearray[stateIndex] = statearray[stateIndex2];
            parent[stateIndex] = parent[stateIndex2];
            countervector[stateIndex] = countervector[stateIndex2];
            maxpath[stateIndex] = maxpath[stateIndex2];
         }
         stateIndex++;
      }
      else delete_edge(os,stateIndex2);
   }
   itemarray.resize( stateIndex );
   statearray.resize( stateIndex );
   parent.resize( stateIndex );
   countervector.resize( stateIndex );
   maxpath.resize( stateIndex );
}

void Trie::assoc_rule_find( ofstream& outcomefile, const double min_conf, set<itemtype>& condition_part,
                            set<itemtype>& consequence_part, const unsigned long union_support) const
{
   set<itemtype>::const_iterator item_it_2;
   itemtype                      item;
   for( set<itemtype>::const_iterator item_it = consequence_part.begin(); item_it != consequence_part.end(); item_it++)
   if( condition_part.empty() || *(--condition_part.end()) < *item_it)
   {
      item = *item_it;
      consequence_part.erase( item );
      condition_part.insert( item );
      if( union_support > countervector[is_included(condition_part)] * min_conf)
      {
         outcomefile << endl;
         for( item_it_2 = condition_part.begin(); item_it_2 != --(condition_part.end()); item_it_2++)
            outcomefile << orderarray[*item_it_2]-1 << ' ';
         outcomefile << orderarray[*item_it_2]-1;
         outcomefile << " ==> ";
         for( item_it_2 = consequence_part.begin(); item_it_2 != --(consequence_part.end()); item_it_2++)
            outcomefile << orderarray[*item_it_2]-1 << ' ';
         outcomefile << orderarray[*item_it_2]-1;
         outcomefile << " ("<<((double) union_support) / countervector[is_included(condition_part)] << ", " << union_support << ')';
      }
      else if( consequence_part.size() > 1 ) assoc_rule_find( outcomefile, min_conf, condition_part, consequence_part, union_support );
      item_it = (consequence_part.insert( item )).first;
      condition_part.erase( item );
   }
}

void Trie::assoc_rule_assist( ofstream& outcomefile, const double min_conf, unsigned long actual_state, set<itemtype>& consequence_part) const
{
   if( consequence_part.size() > 1 )
   {
      set<itemtype> condition_part;
      assoc_rule_find( outcomefile, min_conf, condition_part, consequence_part, countervector[actual_state] );
   }
   vector<unsigned long>::const_iterator it_state = statearray[actual_state].begin();
   for( vector<itemtype>::const_iterator it_item = itemarray[actual_state].begin(); it_item != itemarray[actual_state].end(); it_item++, it_state++)
   {
      consequence_part.insert( *it_item );
      assoc_rule_assist( outcomefile, min_conf, *it_state, consequence_part);
      consequence_part.erase( *it_item );
   }
}
void Trie::write_content_to_file_assist( ofstream& outcomefile, const unsigned long actual_state, const itemtype item_size,
                                         const itemtype actual_size, set<itemtype>& frequent_itemset) const
{
   if( actual_size == item_size )
   {
      for( set<itemtype>::const_iterator it = frequent_itemset.begin(); it != frequent_itemset.end(); it++)
         outcomefile << orderarray[*it]-1 << ' ';
      outcomefile << '(' << countervector[actual_state] << ')'<<endl;
   }
   else
   {
      vector<unsigned long>::const_iterator it_state = statearray[actual_state].begin();
      for( vector<itemtype>::const_iterator it_item = itemarray[actual_state].begin(); it_item != itemarray[actual_state].end(); it_item++, it_state++ )
      if( maxpath[*it_state]+actual_size+1 >= item_size )
      {
         frequent_itemset.insert( *it_item );
         write_content_to_file_assist( outcomefile, *it_state, item_size, actual_size+1, frequent_itemset);
         frequent_itemset.erase( *it_item );
      }
   }
}

Trie::Trie()
{
   countervector.push_back(0);
   maxpath.push_back(0);
   itemarray.resize(1);
   statearray.resize(1);
   parent.push_back(0);   //it could be anything, root doesn't have a parent!
}

/**
  \param frequent_size Size of the frequent itemsets that generate the candidates.
*/
void Trie::candidate_generation( const itemtype& frequent_size )
{
   if( frequent_size == 1 ) candidate_generation_two();
   else if( maxpath[0] == frequent_size )
   {
      set<itemtype> maybe_candidate;
      candidate_generation_assist( 0, frequent_size, 1, maybe_candidate );
   }
}

void Trie::find_candidate( const vector<itemtype>& basket, const itemtype candidate_size, const unsigned long counter)
{
   if( candidate_size == 1 ) find_candidate_one( basket );
   else if( candidate_size == 2 ) find_candidate_two( basket, counter );
   else find_candidate_more( basket, candidate_size, basket.begin(), 0, 0, counter );
}

/**
  \param min_occurrence The threshold of absolute support.
*/
void Trie::delete_infrequent( const unsigned long min_occurrence )
{
   if( maxpath[0] == 0 ) delete_infrequent_one( min_occurrence );
   else if( maxpath[0] == 2 ) delete_infrequent_two( min_occurrence );
   else delete_infrequent_more( min_occurrence );
}

/**
  \param outcomefile The file the output will be written to.
  \param min_conf Confidence threshold.
*/
void Trie::association( ofstream& outcomefile, const double min_conf ) const
{
   outcomefile << "\nAssociation rules:\ncondition ==> consequence (confidence, occurrence)\n";
   set<itemtype> consequence_part;
   assoc_rule_assist( outcomefile, min_conf, 0, consequence_part );
}
/**
  \param basket The given basket.
*/
void Trie::basket_recode( vector<itemtype>& basket ) const
{
   set<itemtype> tempset;
   for( vector<itemtype>::iterator it_basket = basket.begin(); it_basket != basket.end(); it_basket++ )
     if( inv_orderarray[*it_basket+1] ) tempset.insert( inv_orderarray[*it_basket+1] );
   basket.clear();
   basket.insert( basket.end(), tempset.begin(), tempset.end() );
}

unsigned long Trie::node_number() const
{
   if( maxpath[0] == 2 && itemarray[0].size()+1 == itemarray.size() )
      return itemarray.size()+(itemarray.size()-1)*(itemarray.size()-2)/2;
   else return itemarray.size();
}
void Trie::statistics() const
{
   unsigned long mem = itemarray.capacity()+statearray.capacity()+
         countervector.capacity()+maxpath.capacity()+parent.capacity();


   for( unsigned long stateIndex = 0; stateIndex < itemarray.size(); stateIndex++)
      mem += itemarray[stateIndex].capacity() + statearray[stateIndex].capacity();
//   cout<<"\nThe number of nodes of the trie: "<<itemarray.size();
   if( maxpath[0] == 2 && itemarray[0].size()+1 == itemarray.size())
      mem += (itemarray.size()-1)*(itemarray.size()-2)*sizeof(long)/2 + (itemarray.size()-1)*sizeof(unsigned long*);
   cout << "The memory need is: ";
   if( mem/1048576 ) cout << mem/1048576 << " Mbyte + ";
   if( (mem%1048576)/1024 ) cout << (mem%1048576)/1024<<" Kbyte + ";
   cout << mem%1024 <<" byte" << endl;
}
void Trie::write_content_to_file( ofstream& outcomefile ) const
{
   outcomefile << "Frequent 0-itemsets:\nitemset (occurrence)\n";
   outcomefile << "{} ("<< countervector[0] << ')' << endl;
   for( itemtype item_size = 1; item_size < maxpath[0]+1; item_size++ )
   {
      outcomefile << "Frequent " << item_size << "-itemsets:\nitemset (occurrence)\n";
      set<itemtype> frequent_itemset;
      write_content_to_file_assist( outcomefile, 0, item_size, 0, frequent_itemset );
   }
}

void Trie::show_content() const
{
   unsigned long stateIndex;
   itemtype      edgeIndex;
   cout<< "\nSize:" << itemarray.size();
   for( stateIndex = 0; stateIndex < itemarray.size(); stateIndex++)
   {
      cout << endl << "Size of the " << stateIndex << "th state:" << itemarray[stateIndex].size()
      << " its counter: " << countervector[stateIndex] << " longest path: "
      << maxpath[stateIndex] << ", edge point to it: " << parent[stateIndex]<<",leafs:";
      vector<unsigned long>::const_iterator it_state = statearray[stateIndex].begin();
      for( vector<itemtype>::const_iterator it_item = itemarray[stateIndex].begin(); it_item != itemarray[stateIndex].end(); it_item++, it_state++ )
         cout << endl << "Item " << *it_item << " leads to state " << *it_state;
   }
   if( maxpath[0] == 1 && itemarray[0][0] < itemarray.size() )
   {
      cout << endl << "Content of 2D table (counters of itempairs)";
      for( stateIndex = 0; stateIndex < itemarray[0].size()-1; stateIndex++ )
         {
            cout << endl;
            for( edgeIndex =0 ; edgeIndex < itemarray[0].size()-1-stateIndex; edgeIndex++)
               cout << temp_counter_array[stateIndex][edgeIndex]<< ',';
         }
   }
}
Trie::~Trie()
{
}
