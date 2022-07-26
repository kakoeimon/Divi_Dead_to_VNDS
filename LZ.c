#include "stdint.h"
#include "stdio.h"
#include "stdlib.h"


uint8_t  mem1(uint8_t *ptr) { return ((int)ptr[0] << 0); }
uint16_t mem2(uint8_t *ptr) { return (ptr[0] << 0) | (ptr[1] << 8); }
uint32_t   mem4(uint8_t *ptr) { return (ptr[0] << 0) | (ptr[1] << 8) | (ptr[2] << 16) | (ptr[3] << 24); }


uint8_t temp1[0xD0000];
uint8_t temp2[0xE0000];

void LZ_UNCOMPRESS(uint8_t *input, uint32_t input_length, uint8_t *output, uint32_t *output_length) {
	uint8_t ring[0x1000]; uint16_t rinp = 0xFEE; int n;
	for (n = 0; n < 0x1000; n++) ring[n] = 0;
	uint8_t *input_end = input + input_length;
	uint8_t *output_start = output;
	
	while (input < input_end) {
		uint32_t code = *input | 0x100;
		for (input++; code != 1; code >>= 1) {
			if (code & 1) {
				ring[rinp++] = *output++ = *input++;
				rinp &= 0xFFF;
			} else {
				uint8_t l, h;
				if (input >= input_end) break;
				l = *input++; h = *input++;
				uint16_t d = l | (h << 8);
				uint16_t p = (d & 0xFF) | ((d >> 4) & 0xF00);
				uint16_t s = ((d >> 8) & 0xF) + 3;
				while (s--) {
					*output++ = ring[rinp++] = ring[p++];
					p &= 0xFFF; rinp &= 0xFFF;
				}
			}
		}
	}

	if (output_length) *output_length = output - output_start;
}


int main(int argc, char *argv[]) {
	FILE *f = fopen(argv[1], "rb");
	FILE *out = fopen(argv[2], "wb");
	uint32_t i=0;
	char k = 0;
	uint32_t length = 0;
	while(!feof(f))
	{
		fread(&k,sizeof(char),1,f);
		temp1[i] = k;
		//fread(&k,sizeof(char),1,f);
		//printf("a[%d] = %d\n",i,k);
		i++;
	}
	length = i;
	printf("\n");
	if (temp1[0] == 'L' || temp1[1] == 'Z') {
		int size_c, size_u;
		size_c = mem4(temp1 + 2 + 0);
		size_u = mem4(temp1 + 2 + 4);
		length = size_u;
		LZ_UNCOMPRESS(temp1 + 10, size_c, temp2, NULL);
		temp2[size_u] = 0;
	}

	fclose(f);

	for (int i = 0; i < length + 1; i++) {
		//fwrite(&a[i],sizeof(int),1,f);
		fwrite(&temp2[i], sizeof(char), 1, out);
	}
	fclose(out);

	return 0;
}