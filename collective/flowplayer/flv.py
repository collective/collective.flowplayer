# This file is borrowed from the FlashVideo product, by Lukasz Lakomy


#########################################################
## Class that parses file header for FLV (Flash Videos)
## 
## Specification described here: http://osflash.org/flv
##
#########################################################

from struct import *

FLAGS     = {1:'video',
             4:'audio',
             5:'audio + video'}
TAG_TYPES = {'0x8':'audio',
             '0x9':'video',
             '0x12':'meta'}
AMF_TYPES = {'0x0':'number',
             '0x1':'boolean',
             '0x2':'string',
             '0x8':'mixed array',
             '0xb':'date',
             '0xc':'long string',
             }

class FLVHeaderError(Exception):
    pass

class FLVHeader:
    
    def __init__(self):
        self.height = None
        self.width = None
        
    def analyse(self, data):
        metatags = self.analyseContent(data)
        self.height = metatags.get("height",None)
        self.width = metatags.get("width",None)
        return metatags
    
    def bin2float(self, buffer):
        f = unpack(">d",buffer)
        return f[0]
    
    def getHeight(self):
        if self.height:
            return int(self.height)
        else:
            return None
    
    def getWidth(self):
        if self.width:
            return int(self.width)
        else:
            return None
    
    def getFlag(self, flag):
        if FLAGS.has_key(flag):
            return FLAGS[flag]
        else:
            return None
    
    def getTagType(self, tag):
        if TAG_TYPES.has_key(tag):
            return TAG_TYPES[tag]
        else:
            return None
        
    def getAmfType(self, amf_type):
        if AMF_TYPES.has_key(amf_type):
            return AMF_TYPES[amf_type]
        else:
            raise FLVHeaderError, "Unknown AMF Type %s"%amf_type
        
    def analyseContent(self,data):
        """
        """
        signature = data[:3] #always FLV
        if len(data)<=(8+17):
            raise FLVHeaderError,"Data size too small"    
        if not str(signature) == 'FLV':
            raise FLVHeaderError, "This does not appear to be an FLV file"
        metatags = {}
        version = ord(data[3]) #Currently 1 for known FLV files
        flag = ord(data[4]) # 5 - audio+video, 4 audio, 1 video 
        offset = ord(data[5])*(256**3) + ord(data[6])*(256)**2 + ord(data[7])*256 + ord(data[8]) #Total size of header (always 9 for known FLV files)
        header = {'signature':signature,
                  'version':version,
                  'flags':self.getFlag(flag),
                  'offset':offset}
        #print "header", header
        previousTag = ord(data[9])*(256**3) + ord(data[10])*(256)**2 + ord(data[11])*256 + ord(data[12])
        #print previousTag
        start = 13
        #FLV tag
        #print start
        tag_type = hex(ord(data[start]))
        tag_type = self.getTagType(tag_type)
        #print tag_type
        tag_size = ord(data[start+1])*(256)**2 + ord(data[start+2])*256 + ord(data[start+3]) #Size of Body (total tag size - 11)
        #print type(tag_size)
        timestamp = ord(data[start+4])*(256)**2 + ord(data[start+5])*256 + ord(data[start+6]) #Timestamp of tag (in milliseconds) 0
        timestamp2 = ord(data[start+7]) #Timestamp extension to form a uint32_be. This field has the upper 8 bits.
        stream_id = ord(data[start+8])*(256)**2 + ord(data[start+9])*256 + ord(data[start+10]) #Always 0
        s = start + 11
        #print s
        end = s + tag_size
        #print end
        body = data[s:end]
        meta_tag = {'type'         :tag_type,
                    'size'         :tag_size,
                    'timestamp'    :timestamp,
                    'ext_timestamp':timestamp2,
                    'stream_id'    :stream_id,
                    'body'         :body
                    }
        #print meta_tag
        amf1_start = 0
        #Each tag contains 2 AMF packets
        amf1_type = hex(ord(body[amf1_start]))
        amf1_type = self.getAmfType(amf1_type)
        if amf1_type != 'string':
            raise FLVHeaderError,"First AMF tag is not a string"
        amf1_len = ord(body[amf1_start+1])*256 + ord(body[amf1_start+2])
        #print amf1_len
        amf1_val = body[amf1_start+2:amf1_start+2+amf1_len+1]
        #print amf1_val
        amf2_start = amf1_start+2+amf1_len+1
        #print "amf2_start",amf2_start
        amf2_type = hex(ord(body[amf2_start]))
        amf2_type = self.getAmfType(amf2_type)
        #print "amf2_type",amf2_type
        if amf2_type != 'mixed array':
            raise FLVHeaderError,"Second AMF tag is not an array"
        max_index = ord(body[amf2_start+1])*(256**3) + ord(body[amf2_start+2])*(256**2) + ord(body[amf2_start+3])*(256) + ord(body[amf2_start+4])
        #print "max_index",max_index
        array_start = amf2_start+5
        for index in range(max_index):
            #print "\narray_start",array_start
            element_len = ord(body[array_start])*256 + ord(body[array_start+1])
            #print "element_len: ",element_len
            element_name = body[array_start+2:array_start+2+element_len]
            #print "element_name: ",element_name            
            value_type = hex(ord(body[array_start+element_len+2]))
            #print "value_type",value_type
            value_type = AMF_TYPES[value_type]
            #print "element_val_type",value_type
            if value_type == 'number':                
                element_val = body[array_start+element_len+2:array_start+element_len+2+9]
                value_value = element_val[1:] #8 bit double
                value_value = self.bin2float(value_value)
                #print "value_value",value_value
                array_start = array_start+element_len+2+9
            elif value_type == 'string':            
                value_len = ord(body[array_start+element_len+3])*256 + ord(body[array_start+element_len+4])
                #print "value_len: ",value_len
                value_value = str(body[array_start+element_len+5:array_start+element_len+5+value_len])
                #print "value_value",value_value
                array_start = array_start+element_len+5+value_len
            elif value_type == 'date':
                #I dont need that
                #Date is represented as 0x0B, then a double, then an int. 
                value_value = None
                array_start = array_start+3+element_len+8+2
            else:
                break
            metatags[element_name] = value_value
            
        if hex(ord(body[array_start])) == '0x0' and\
           hex(ord(body[array_start+1])) == '0x0' and\
           hex(ord(body[array_start+2])) == '0x9':
            #End of mixed array - OK
            pass
        else:
            pass
            #raise FLVHeaderError, "Wrong end of mixed array: %s%s%s"%(hex(ord(body[array_start])),
            #                                                          hex(ord(body[array_start+1])),
            #                                                          hex(ord(body[array_start+2])))
        return metatags