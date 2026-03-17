import assert from 'node:assert/strict'
import test from 'node:test'
import { tierFromPlaycount } from '../src/lib/tierMapping'

test('playcount 2 and 3 map to Light', () => {
  assert.equal(tierFromPlaycount(2), 'Light')
  assert.equal(tierFromPlaycount(3), 'Light')
})
