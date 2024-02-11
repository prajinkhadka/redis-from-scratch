from dataclasses import dataclass 

@dataclass
class RedisConfig:
    directory: str 
    dbfilename: str
