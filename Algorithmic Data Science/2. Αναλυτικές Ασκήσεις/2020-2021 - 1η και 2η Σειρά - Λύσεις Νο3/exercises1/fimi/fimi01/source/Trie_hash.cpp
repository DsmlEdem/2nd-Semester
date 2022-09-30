/***************************************************************************
                          trie_hash.cpp  -  description
                             -------------------
    begin                : cs dec 26 2002
    copyright            : (C) 2002 by Ferenc Bodon
    email                : bodon@mit.bme.hu
 ***************************************************************************/

#include <cstdlib>
#include <iostream>
using namespace std;
#include "Trie_hash.hpp"

/**
      \param stateIndex The node that has to be altered.
  */
void Trie_hash::from_hash_to_normal( const unsigned long stateIndex )
{
   itemtype item_index1 = 0, item_index2 = 1;
   type_vector[stateIndex] = true;
   itemarray[stateIndex].resize( statearray[stateIndex][0] );
   while( item_index1 < itemarray[stateIndex].size() )
   {
      if( statearray[stateIndex][item_index2] )
      {
         itemarray[stateIndex][item_index1] = item_index2;
         statearray[stateIndex][item_index1] = statearray[stateIndex][item_index2];
         item_index1++;
      }
      item_index2++;
   }
   statearray[stateIndex].resize(itemarray[stateIndex].size());
}

/**
     \param stateIndex The node that has to be altered.
  */
void Trie_hash::from_normal_to_hash( const unsigned long stateIndex )
{
   type_vector[stateIndex] = false;
   vector<unsigned long> temp_allapotvektor( statearray[stateIndex] );
   statearray[stateIndex].assign( hash_modulus, 0 );
   statearray[stateIndex][0] = itemarray[stateIndex].size();
   for( itemtype item_index = 0; item_index < itemarray[stateIndex].size(); item_index++)
      statearray[stateIndex][itemarray[stateIndex][item_index]] = temp_allapotvektor[item_index];
   itemarray[stateIndex].clear();
}

void Trie_hash::delete_edge( const unsigned long fromState, const unsigned long toState )
{
   if( type_vector[fromState] ) return Trie::delete_edge( fromState, toState );
   else
   {
      for( itemtype edge_index = 1; edge_index < hash_modulus; edge_index++ )
         if (statearray[fromState][edge_index] == toState)
         {
            statearray[fromState][edge_index] = 0;
            if( itemarray[fromState].size() < child_threshold+1 ) from_hash_to_normal( fromState );
            if( itemarray[fromState].empty() )
            {
               maxpath[fromState] = 0;
               max_path_set( parent[fromState] );
            }
         }
   }
}

void Trie_hash::max_path_set( const unsigned long stateIndex )
{
   if (type_vector[stateIndex]) Trie::max_path_set(stateIndex);
   else
   {
      itemtype temp_max_path=0;
      for (unsigned short edge_index=1;edge_index<hash_modulus;edge_index++)
        if (statearray[stateIndex][edge_index] && temp_max_path<maxpath[statearray[stateIndex][edge_index]]+1 )
           temp_max_path=maxpath[statearray[stateIndex][edge_index]]+1;
      if (maxpath[stateIndex] != temp_max_path )
      {
         maxpath[stateIndex] = temp_max_path;
         if( stateIndex ) max_path_set( parent[stateIndex] );
      }
   }
}

void Trie_hash::add_empty_state( const unsigned long fromState, const itemtype item, const unsigned long counter )
{
  type_vector.push_back(true);
  Trie::add_empty_state(fromState, item, counter);
}

unsigned long Trie_hash::is_included( const set<itemtype>& an_itemset ) const
{
   unsigned long hol = 0;
   vector<itemtype>::const_iterator it_itemvector;
   for (set<itemtype>::const_iterator item_it = an_itemset.begin();item_it != an_itemset.end(); item_it++)
   {
      if( type_vector[hol] )
      {
         it_itemvector = lower_bound( itemarray[hol].begin(), itemarray[hol].end(), *item_it );
         if (it_itemvector != itemarray[hol].end() && *it_itemvector == *item_it)
            hol = statearray[hol][it_itemvector-itemarray[hol].begin()];
         else return 0;
      }
      else if( (hol = statearray[hol][*item_it]) == 0 ) return 0;
   }
   return hol;
}


void Trie_hash::candidate_generation_assist( unsigned long actual_state, const itemtype frequent_size,
                                             const itemtype actual_size, set<itemtype>& maybe_candidate )
{
   if ( type_vector[actual_state] ) Trie::candidate_generation_assist( actual_state, frequent_size, actual_size, maybe_candidate);
   else
   {
      itemtype edge_index;
      if( actual_size == frequent_size )
      {
         from_hash_to_normal( actual_state );
         Trie::candidate_generation_assist( actual_state, frequent_size, actual_size, maybe_candidate );
         for( edge_index = 0; edge_index < itemarray[actual_state].size(); edge_index++)
           if( itemarray[statearray[actual_state][edge_index]].size() > child_threshold )
              from_normal_to_hash( statearray[actual_state][edge_index] );
         from_normal_to_hash( actual_state );
      }
      else
      {
         for( edge_index = 1; edge_index < hash_modulus; edge_index++) if( statearray[actual_state][edge_index] )
         {
            maybe_candidate.insert( edge_index );
            candidate_generation_assist( statearray[actual_state][edge_index], frequent_size, actual_size+1, maybe_candidate);
            maybe_candidate.erase( edge_index );
         }
      }
   }
}

void Trie_hash::find_candidate_more( const vector<itemtype>& basket, const itemtype candidate_size,
                                     vector<itemtype>::const_iterator it_basket, const unsigned long actual_state,
                                     const itemtype actual_size, const unsigned long counter)
{
   if( candidate_size == actual_size )
      countervector[actual_state] += counter;
   else
   {
      if( type_vector[actual_state] ) Trie::find_candidate_more( basket, candidate_size, it_basket, actual_state, actual_size,counter );
      else for (;candidate_size < basket.end()-it_basket+actual_size+1; it_basket++)
              if( statearray[actual_state][*it_basket] && maxpath[statearray[actual_state][*it_basket]]+actual_size+1 == candidate_size)
                 find_candidate_more( basket, candidate_size, it_basket+1, statearray[actual_state][*it_basket], actual_size+1,counter );

   }
}

void Trie_hash::delete_infrequent_one( const unsigned long min_occurrence )
{
  Trie::delete_infrequent_one( min_occurrence );
  hash_modulus = itemarray.size();
}

void Trie_hash::delete_infrequent_two( const unsigned long min_occurrence )
{
  Trie::delete_infrequent_two( min_occurrence );
  for( unsigned long stateIndex = 0; stateIndex < itemarray.size(); stateIndex++ )
     if( itemarray[stateIndex].size() > child_threshold ) from_normal_to_hash( stateIndex );
     else type_vector[stateIndex] = true;
}

void Trie_hash::delete_infrequent_more( const unsigned long min_occurrence )
{
   unsigned long stateIndex = 1,
                 stateIndex2,
                 os;

   for( stateIndex2 = 1; stateIndex2 < itemarray.size(); stateIndex2++ )
   {
      os = parent[stateIndex2];
      if( countervector[stateIndex2] >= min_occurrence )
      {
         if( stateIndex != stateIndex2)
         {
            vector<unsigned long>::iterator it_state;
            if( type_vector[os] ) it_state = lower_bound( statearray[os].begin(), statearray[os].end(), stateIndex2 );
            else it_state = lower_bound( statearray[os].begin()+1, statearray[os].end(), stateIndex2);
            *it_state = stateIndex;
            itemarray[stateIndex] = itemarray[stateIndex2];
            statearray[stateIndex] = statearray[stateIndex2];
            parent[stateIndex] = parent[stateIndex2];
            countervector[stateIndex] = countervector[stateIndex2];
            type_vector[stateIndex] = type_vector[stateIndex2];
            maxpath[stateIndex] = maxpath[stateIndex2];
         }
         stateIndex++;
      }
      else delete_edge( os, stateIndex2 );
   }
   itemarray.resize( stateIndex );
   statearray.resize( stateIndex );
   parent.resize( stateIndex );
   countervector.resize( stateIndex );
   maxpath.resize( stateIndex );
   type_vector.resize( stateIndex );
}


void Trie_hash::assoc_rule_assist( ofstream& outcomefile, const double min_conf,
                                   unsigned long actual_state, set<itemtype>& consequence_part) const
{
   if( type_vector[actual_state] ) Trie::assoc_rule_assist( outcomefile, min_conf, actual_state,consequence_part );
   else
   {
      if( consequence_part.size() > 1 )
      {
         set<itemtype> condition_part;
         assoc_rule_find(outcomefile, min_conf, condition_part, consequence_part, countervector[actual_state]);
      }

      itemtype edge_index;
      for( edge_index = 1; edge_index < hash_modulus; edge_index++)
         if( statearray[actual_state][edge_index] )
         {
            consequence_part.insert( edge_index );
            assoc_rule_assist( outcomefile, min_conf, statearray[actual_state][edge_index], consequence_part);
            consequence_part.erase( edge_index );
         }
   }
}

void Trie_hash::write_content_to_file_assist( ofstream& outcomefile, const unsigned long actual_state,
                                              const itemtype item_size, const itemtype actual_size,
                                              set<itemtype>& frequent_itemset ) const
{
   if (type_vector[actual_state] || actual_size == item_size)
      Trie::write_content_to_file_assist( outcomefile, actual_state, item_size, actual_size, frequent_itemset );
   else for( itemtype item_index = 1; item_index < hash_modulus; item_index++ )
           if( statearray[actual_state][item_index] && maxpath[statearray[actual_state][item_index]]+actual_size+1 >= item_size)
           {
              frequent_itemset.insert( item_index );
              write_content_to_file_assist( outcomefile, statearray[actual_state][item_index], item_size, actual_size+1, frequent_itemset );
              frequent_itemset.erase( item_index );
           }
}

Trie_hash::Trie_hash( const itemtype child_threshold_in ):Trie()
{
   child_threshold = child_threshold_in;
   type_vector.push_back( true );
}
void Trie_hash::statistics() const
{
   unsigned long mem = itemarray.capacity() + statearray.capacity()+
                       countervector.capacity()+ maxpath.capacity()+ parent.capacity()+type_vector.capacity();

   for( unsigned long stateIndex = 0; stateIndex < itemarray.size(); stateIndex++)
       if( type_vector[stateIndex] ) mem += itemarray[stateIndex].capacity() + statearray[stateIndex].capacity();
    else mem += hash_modulus * sizeof(long);
    if( maxpath[0] == 2 && itemarray[0].size()+1 == itemarray.size() )
       mem += (itemarray.size()-1) * (itemarray.size()-2) * sizeof(long)/2+(itemarray.size()-1) * sizeof(unsigned long*);
//   cout<<"\nA szofa allapotainak szama: "<<itemarray.size();
   cout << "The memory need is: ";
   if (mem/1048576) cout << mem/1048576 <<" Mbyte + ";
   if ((mem%1048576)/1024) cout << (mem%1048576)/1024 << " Kbyte + ";
   cout<<mem%1024 << " byte" << endl;
}

void Trie_hash::show_content() const
{
   unsigned long stateIndex;
   itemtype      edge_index;

   cout << "\nSize:" << itemarray.size();
   for( stateIndex = 0; stateIndex < itemarray.size(); stateIndex++)
   {
      cout << '\n' << stateIndex << "-id állapot mérete:" << itemarray[stateIndex].size()
           << " számlálója: " << countervector[stateIndex] << " leghosszab utja: "<<maxpath[stateIndex]
           << ", ra mut. állapot" << parent[stateIndex]<<" ,tipusa:";
      if( type_vector[stateIndex] )
      {
         cout << " normális csúcs, levelei:";
         for( edge_index = 0; edge_index < itemarray[stateIndex].size(); edge_index++)
            cout << "\n " << itemarray[stateIndex][edge_index] << "hatasara" << statearray[stateIndex][edge_index];
      }
      else
      {
         cout << " hash tábla, levelei:";
         for( edge_index = 1; edge_index < hash_modulus; edge_index++ )
            if( statearray[stateIndex][edge_index] ) cout << "\n " << edge_index << "hatasara" << statearray[stateIndex][edge_index];
      }
   }
   if ( maxpath[0] == 1 && itemarray[0].size()+1 < itemarray.size())
   {
      cout << endl << "Content of 2D table (counters of itempairs)";
      for( stateIndex = 0; stateIndex < itemarray[0].size()-1; stateIndex++ )
      {
         cout << endl;
         for( edge_index = 0; edge_index < itemarray[0].size()-1-stateIndex; edge_index++ )
            cout << temp_counter_array[stateIndex][edge_index] << ',';
      }
   }
}
