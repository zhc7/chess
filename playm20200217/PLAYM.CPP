#include <stdio.h>
#include <string.h>

void countzero( char* );
void diffrentchars( char*, char* );

void main( int argc, char** argv )
{

    if ( argc < 2 )
    {
	printf( "usage: PLAYM <*.txt> [step]" );
	return;
    }

    FILE* f=fopen( argv[1], "rt" );

    if ( stricmp( argv[2], "3" ) == 0 )
    {
	int size = fseek( f, 0, SEEK_END );
	if ( size == 0 ) {
	long pos = ftell( f );
	if ( pos >= 0 )
	{
		size = pos;
		if ( fseek( f, 0, SEEK_SET ) == 0 )
		{
		char* buf = new char[size+1];
		if ( buf != NULL )
		{
			if ( fread( buf, size, 1, f ) != 0 )
			{
				buf[size] = 0;
				char* p = buf;
				while( *p != 0 )
				{
					if ( *p == ',' && p[1] == ';' )
                                        	strcpy( p, p+1 );
					else
						p ++;
				}
				printf( buf );
			}
			delete buf;
		}	}
	}	}
    } else {

    char lns[255];

    int count = 0;
    char _1stln[255];
    while ( fgets( lns, 255, f ) != NULL )
    {
	if ( stricmp( argv[2], "1" ) == 0 )
	{

	char* p=lns;
	while ( *p != '0' && p[0] != 0 )
		p++;
	if ( strlen( p ) > 0 )
	{

		while ( *p != ' ' && *p != '\n' && p[0] != 0 )
			p++;
		*p = 0;
		printf( lns );
		printf( "\n" );

	}}
	else
	if ( stricmp( argv[2], "2" ) == 0 )
	{
	       count ++;
	       if ( count == 1 )
	       {
		     countzero( lns );
	       } else {
		     diffrentchars( _1stln, lns );
	       }
		strcpy( _1stln, lns );
	}
    }

    }	fclose( f );
}

void countzero( char* ln )
{
	int cou = 0;
	char* p = ln;
	while ( *p != 0 )
	{
		cou = 0;
		while ( *p == '0' ) { cou ++; p++; }
		printf( "%d", cou );

		if ( *p != 0 ) printf( "," );

		if ( *p == '\n' ) {
			printf( ";" );
			break;
		}

		while ( *p != '0' ) {
		printf( "%c", *p );  p++; }

		if ( *p != 0 ) printf( "," );
	}
}

void diffrentchars( char* old, char* n )
{
	for ( int i=0; i<strlen(old); i++ )
	{
		if ( old[i] != n[i] )
		{
			printf( "%d,%c,", i+1, n[i] );
		}
	}
			printf( ";" );
}