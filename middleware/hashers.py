"""
hashers

A module to make hashers objects and work easily

Algorithms to hash implemented:
    SHA1
    SHA256
    SHA512
    IP -> uses shake_128 algorithm
    IP2 -> uses shake_256 algorithm
    PASSWORD -> uses pbkdf2_hmac algorithm,
    
    NOTE: if None algorithm is asked, them the default method for hash of the machine is used
"""

from hashlib import sha1,sha256,sha512,shake_128,shake_256,pbkdf2_hmac

class Hasher:
    
    """
    abstraction of a hasher object
    """
    
    _state = None
    
    def __init__(self):
        pass
    
    def _reset(self):
        """
        restart the internal state
        WARNING! DON'T USE OUT OF THIS CLASS
        """
        raise NotImplementedError()
    
    def hash(self,object,encoding='utf-8'):
        """
        returns the sha1 hash for the given object
        
        if type of object is string, then is encoding with the 'encoding' parameter
        """
        self._reset()
        
        if isinstance(object,str):
            
            self._state.update(bytes(object,encoding))
            return int(self._state.digest().hex(),16)
        
        self._state.update(bytes(object))
        
        return int(self._state.digest().hex(),16)
    
class HasherSHA1(Hasher):
   
    """
    An object that returns that stores the history to make hashes with the 'sha1' algorithm
    """
    
    def _reset(self):
        self._state = sha1()
        pass
   
    pass

class HasherSHA256(Hasher):
       
    """
    An object that returns that stores the history to make hashes with the 'sha256' algorithm
    """
    
    def _reset(self):
        self._state = sha256()
    
class HasherSHA512:
       
    """
    An object that returns that stores the history to make hashes with the 'sha512' algorithm
    """
    
    def _reset(self):
        self._state = sha512()
    
class IpHasher(Hasher):
    
    """
    A hasher object intended to ip address
    """
    
    def __init__(self):
        pass
    
    def _reset(self):
        self._state = shake_128()
        
    def hash(self,object,encoding='utf-8'):
        
        self._reset()
        
        if isinstance(object,str):
        
            self._state.update(bytes(object,encoding))
            return int(self._state.digest(len(object)).hex(),16)
        
        self._state.update(object)
        
        return int(self._state.digest(len(object)).hex(),16)
    
class IpHasher2(IpHasher):
    
    """
    Another implementation to hash ip address
    """
    
    def _reset(self):
        self._state = shake_256()
        pass
    

class PasswordHasher(Hasher):
    
    """
    A hasher intended to hash passwords
    
    algorithm: method to use for the hash
    iterations: count of iteration to generate the hash
    
    ALGORITHMS GUARANTED:
        SHA1
        SHA256
        SHA512
    """
    
    def __init__(self,algorithm='sha1',salt=1,iterations=10):
        
        self._algorithm = algorithm
        self._salt = bytes(salt)
        self._iterations = iterations
        
    def hash(self,object,encoding='utf-8'):
    
        if isinstance(object,str):
            hash_value = pbkdf2_hmac(self._algorithm,bytes(object,encoding),self._salt,self._iterations)
            return int(hash_value.hex(),16)
    
        hash_value = pbkdf2_hmac(self._algorithm,bytes(object),self._salt,self._iterations)
        
        return int(hash_value.hex(),16)
    
    def set_salt(self,salt):
        
        if isinstance(salt,str):
            self._salt = bytes(salt,'utf-8')
        
        else:
            self._salt = bytes(salt)
        
    def set_iterations(self,iterations):
        self._iterations = iterations
    
class DefaultHasher(Hasher):
    
    """
    A hasher that use the default method to get the hash of an object
    """
    
    def __init__(self):
        pass
    
    def hash(self,object,encoding='utf-8'):
    
        if isinstance(object,str):
            return hash(bytes(object,encoding))
    
        return hash(object)

ALGORITHMS = {
    1: HasherSHA1,
    2: HasherSHA256,
    3: HasherSHA512,
    4: IpHasher,
    5: IpHasher2,
    6: PasswordHasher,
    0: DefaultHasher
}

BITS_MEMORYS = {
    HasherSHA1: 1,
    HasherSHA256: 256,
    HasherSHA512: 512,
    IpHasher: 128,
    IpHasher2: 256,
    PasswordHasher: 512,
    DefaultHasher: 512
}

def GetHasher(algorithm=0):
    
    """
    returns a hasher object for the algorithm specified
    
    OPTIONS:
        1 -> SHA1
        2 -> SHA256
        3 -> SHA512
        4 -> IP
        5 -> IP2
        6 -> PASSWORD
        0 -> DEFAULT
        
    """
    
    if not algorithm in ALGORITHMS.keys():
        raise Exception(f"Does not exists a hasher for the algorithm '{algorithm}'")
    alg = ALGORITHMS[algorithm]
    return alg() , BITS_MEMORYS[alg]