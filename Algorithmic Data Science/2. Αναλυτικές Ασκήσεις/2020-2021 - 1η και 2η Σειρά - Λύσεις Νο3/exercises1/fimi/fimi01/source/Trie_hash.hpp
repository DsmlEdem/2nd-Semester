/***************************************************************************
                          trie_hash.h  -  description
                             -------------------
    begin                : cs dec 26 2002
    copyright            : (C) 2002 by Ferenc Bodon
    email                : bodon@mit.bme.hu
 ***************************************************************************/

#ifndef TRIE_HASH_H
#define TRIE_HASH_H

#include "Trie.hpp"


/**
  *@author Ferenc Bodon
  */

class Trie_hash : public Trie
{
public:

   Trie_hash( const itemtype child_threshold_in=5 );
   void statistics() const;
   void show_content() const;

private:

   //! Alters a node from hash table to normal node.
   void from_hash_to_normal( const unsigned long state_index );

   //! Alters a node from normal node to hash table.
   void from_normal_to_hash( const unsigned long state_index );

   void delete_edge( const unsigned long from_state, const unsigned long to_state );
   void max_path_set( const unsigned long state_index );
   void add_empty_state( const unsigned long from_state, const itemtype item, const unsigned long counter );
   unsigned long is_included( const set<itemtype>& an_itemset ) const;
   void delete_infrequent_one( const unsigned long min_occurrence );
   void delete_infrequent_two( const unsigned long min_occurrence );
   void delete_infrequent_more( const unsigned long min_occurrence );
   void candidate_generation_assist( unsigned long actual_state,const itemtype frequent_size,
                                     const itemtype actual_size, set<itemtype>& maybe_candidate );
   void find_candidate_more( const vector<itemtype>& basket, const itemtype candidate_size,
                             vector<itemtype>::const_iterator it_basket, const unsigned long actual_state,
                             const itemtype actual_size, const unsigned long counter=1 );
   void assoc_rule_assist( ofstream& outcomefile,const double min_conf, unsigned long actual_state, set<itemtype>& consequence_part ) const;
   void write_content_to_file_assist( ofstream& outcomefile, const unsigned long actual_state,
                                      const itemtype item_size, const itemtype actual_size, set<itemtype>& frequent_itemset ) const;

   /** It stores the type of the nodes.
     *
     * If type_vector[i] is true, the i<sup>th</sup> node is an original node,
     * otherwise it is a hash table.
     */
   vector<bool> type_vector;

   /** \brief When the child number of a node is higher than child_threshold it is altered to hash table.*/
   itemtype child_threshold;

   /** The modulus of the hash table.
     *
     * Since hash tables have to be perfect the hash modulus equals the number of frequent items.
     */
   itemtype hash_modulus;


};

#endif
