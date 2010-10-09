#pragma once

#include "algorithm.hpp"
#include "Integer.hpp"
#include "SampleBuffer.hpp"

struct TileCache {
	private:
		typedef Vec<2, int> Key;
		typedef SampleBuffer Tile;

		struct Node {
			Node(Key const & key, TileCache * cache) :
				key(key),
				value(cache->get_tile_stride()),
				next(0)
			{ }

			bool operator < (Key const & right) const {
				if (key.x() < right.x()) { return true; }
				if (right.x() < key.x()) { return false; }

				return key.y() < right.y();
			}

			bool operator < (Node const & right) const {
				return *this < right.key;
			}

			// NOTE: This works like std::lower_bound except it returns the
			// node BEFORE the first node >= key, or null if that would be the
			// first one (and the last node in the list if there is no node >=
			// key).

			static inline Node * lower_bound(Node * next, Key const & key) {
				Node * prev = 0;
				for (; next && *next < key; prev = next, next = next->next) { ; }
				return prev;
			}

			// NOTE: New items are in inserted sorted in increasing order.
			// This returns the first element of the list, which may be
			// different than start.

			static inline Node * insert(Node * start, Node * node) {
				Node * prev = lower_bound(start, node->key);

				if (prev) {
					node->next = prev->next;
					prev->next = node;
					return start;
				}
				else {
					node->next = start;
					return node;
				}
			}

			static inline uint32 size(Node const * start) {
				uint32 i = 0;
				for (; start; start = start->next) { ++i; }
				return i;
			}

			static inline void free(Node * next) {
				for (Node * prev = 0; next; prev = next, next = next->next)
					{ delete prev; }
			}

			Key key;
			Tile value;

			Node * next;
		};

		struct Bucket {
			Bucket() : start(0), size(0) { }

			Node * start; 
			uint32 size;
		};

	public:
		TileCache(int tile_length, int sample_rate) :
			buckets_(0), node_count_(0), bucket_count_(0),
			tile_length_(tile_length), sample_rate_(sample_rate),
			tile_stride_(tile_length * sample_rate),
			cached_(0)
		{ rebucket(1); } // TODO: Do we want to be able to default construct these without any heap overhead?

		~TileCache() {
			Bucket * end = buckets_ + bucket_count_;

			for (Bucket * b = buckets_; b != end; ++b)
				{ Node::free(b->start); }

			delete [] buckets_;
		}

		Tile * find_tile(Key const & key) {
			if (cached_ && cached_->key == key) { return &cached_->value; }

			Bucket * bucket = get_bucket(key);
			if (!bucket) { return 0; }

			Node * node = Node::lower_bound(bucket->start, key);
			node = node ? node->next : bucket->start;
			if (node && node->key == key) { return cache(node); }

			return 0;
		}

		Tile * get_tile(Key const & key) {
			if (cached_ && cached_->key == key) { return &cached_->value; }

			Bucket * bucket = get_bucket(key);
			Node * node = Node::lower_bound(bucket->start, key);
			Node ** out = node ? &node->next : &bucket->start;

			if (*out && (*out)->key == key) { return cache(*out); }

			*out = Node::insert(*out, new Node(key, this));
			cache(*out);
			++bucket->size;
			++node_count_;
			if (node_count_ / bucket_count_ > 8) { rebucket(bucket_count_ + 1); }
			return &cached_->value;
		}

	int get_tile_length() const { return tile_length_; }
	int get_sample_rate() const { return sample_rate_; }
	int get_tile_stride() const { return tile_stride_; }

	template <class F>
	void for_each_tile(F f) const {
		for (Bucket * b = buckets_, * end = b + bucket_count_; b != end; ++b) {
			for (Node * n = b->start; n; n = n->next) {
				f(*this, n->key, n->value);
			}
		}
	}

	private:
		TileCache(TileCache const &); // no copying

		static inline uint32 hash_key(Key const & key) {
			// TODO: Make a non-shitty hash
			return static_cast<uint32>(key.x()) * 1023
				^ static_cast<uint32>(key.y());
		}

		Tile * cache(Node * node) { cached_ = node; return &node->value; }

		static inline uint32 get_bucket_index(Key const & key, uint32 count) {
			return hash_key(key) % count;
		}

		uint32 get_bucket_index(Key const & key) {
			return get_bucket_index(key, bucket_count_);
		}

		Bucket * get_bucket(Key const & key) {
			return buckets_ + get_bucket_index(key);
		}

		void rebucket(uint32 count) {
			Bucket * new_buckets = new Bucket[count];

			Bucket * end = buckets_ + bucket_count_;
			for (Bucket * bucket = buckets_; bucket != end; ++bucket) {
				Node * next = 0;

				for (Node * node = bucket->start; node; node = next) {
					next = node->next;
					Node * & start = new_buckets[get_bucket_index(node->key, count)].start;
					start = Node::insert(start, node);
				}
			}

			end = new_buckets + count;
			for (Bucket * bucket = new_buckets; bucket != end; ++bucket) {
				bucket->size = Node::size(bucket->start);
			}

			Bucket * temp = buckets_;
			buckets_ = new_buckets;
			bucket_count_ = count;
			delete [] temp;
		}

		Bucket * buckets_;
		uint32 node_count_, bucket_count_;

		int tile_length_, sample_rate_, tile_stride_;
		Node * cached_;
};
