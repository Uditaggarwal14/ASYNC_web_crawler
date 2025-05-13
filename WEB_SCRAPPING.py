MOD = 10**9 + 7

class Solution(object):
    def lengthAfterTransformations(self, s, t):
        freq = [0] * 26
        for ch in s:
            distance = ord('z') - ord(ch)
            freq[distance] += 1

        for _ in range(t):
            new_freq = [0] * 26
            for j in range(25):  # 'a' to 'y'
                new_freq[j + 1] = (new_freq[j + 1] + freq[j]) % MOD
                # 'z' → 'ab'
                new_freq[0] = (new_freq[0] + freq[25]) % MOD
                new_freq[1] = (new_freq[1] + freq[25]) % MOD
                freq = new_freq
        return sum(freq) % MOD
    
solution = Solution()
print(solution.lengthAfterTransformations("abcyy", 2))  # Example usage
