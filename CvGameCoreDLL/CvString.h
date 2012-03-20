#pragma once

#ifndef CvString_h
#define CvString_h

#include <string>

//#pragma warning( push )
//#pragma warning( disable:4996 )	// stricmp warning

//
// simple string classes, based on stl, but with a few helpers
//
// DON'T add any data members or virtual functions to these classes, so they stay the same size as their stl counterparts
//
// Mustafa Thamer
// Firaxis Games, copyright 2005
//
// ---------------------------------------------------
// * 2012-02-xx lesslol 
//
//  Reduce memory allocation and (duplicated) string copy
// - format method changed to nested (child) class
//		effectively to pass as a parameter or to use as a r-value
// - formatv method changed to modify local buffer directly
//		reduce alloc and copy operaton
// - methods (AppendFormat, appendfmt) added
// - class CvStaticString added
//
// Some other modification
// - changed char vs. unicode convertion to use kernel api directly (MultiByteToWideChar, WideCharToMultiByte) 
// - useful method (CvWStringBuffer::erase), code optimization ...
//

inline int safe_wcscmp(const wchar *s1, const wchar *s2) { return ::wcscmp( s1 ? s1 : L"", s2 ? s2 : L"" ); }
inline int safe_wcslen(const wchar *s) { return (s ? ::wcslen(s) : 0); }

// wide string
class CvWString : public std::wstring
{
public:
	CvWString() : std::wstring() {}
	CvWString(const CvWString& s)	: std::wstring((const std::wstring&)s) { }
	CvWString(const wchar* s)		: std::wstring((s)?s:L"") { } // lol: need to check NULL
	CvWString(const wchar* s, int n): std::wstring(s, n) { }
	CvWString(const std::wstring& s): std::wstring(s) { }
	CvWString(const char* s)		: std::wstring( ) { Copy(s); }
	CvWString(const std::string& s) : std::wstring( ) { Copy(s.c_str()); }
	CvWString(int count, wchar ch)  : std::wstring(count, ch) { }
#ifndef _USRDLL
	// FString conversion, if not in the DLL
	CvWString(const FStringA& s) { Copy(s.GetCString()); }
	CvWString(const FStringW& s) { assign(s.GetCString()); }
#endif
	~CvWString() {}

	void Convert(const std::string& s) { Copy(s.c_str()); }
	void Copy(const char* s);
	bool IsEmpty() const { return empty();	}
	int CompareNoCase( const wchar* lpsz ) const { return _wcsicmp(lpsz, c_str()); }
	int CompareNoCase( const wchar* lpsz, int iLength ) const { return _wcsnicmp(lpsz, c_str(), iLength);  }

	// FString compatibility
	const wchar* GetCString() const	{ return c_str(); }

	// implicit conversion
	operator const wchar*() const 	{ return c_str(); }							

	// operators
	wchar& operator[](int i) { return std::wstring::operator[](i);	}
	wchar& operator[](std::wstring::size_type i) { return std::wstring::operator[](i);	}
	const wchar operator[](int i) const { return std::wstring::operator[](i);	}
	const CvWString& operator=( const wchar* s) { if (s) assign(s); else clear();	return *this; }	
	const CvWString& operator=( const std::wstring& s) { assign(s.c_str(), s.length());	return *this; }	
	const CvWString& operator=( const std::string& w) { Copy(w.c_str());	return *this; }	
	const CvWString& operator=( const CvWString& w) { assign(w.c_str(), w.length());	return *this; }	
#ifndef _USRDLL
	// FString conversion, if not in the DLL
	const CvWString& operator=( const FStringW& s) { assign(s.GetCString());	return *this; }	
	const CvWString& operator=( const FStringA& w) { Copy(w.GetCString());	return *this; }	
#endif
	const CvWString& operator=( const char* w) { Copy(w); return *this; }	

	void Format( LPCWSTR lpszFormat, ... );
	void AppendFormat( LPCWSTR lpszFormat, ... );
	
	CvWString& appendSafe(const wchar* s) { if(s) append(s, ::wcslen(s)); return *this; }

	// MOD by lol
	class format;

	// static helpers
	static bool formatv(CvWString& out, const wchar * fmt, va_list args);
	static bool appendfmtv(CvWString& out, const wchar * fmt, va_list args);
};


class CvWString::format : public CvWString
{
public:
	format(const wchar* fmt, ...) : CvWString()
	{
		va_list args;
		va_start(args, fmt);
		formatv(*this, fmt, args);
		va_end(args);
	}
	~format() { };
private:
	format() { };
};


inline CvWString operator+( const CvWString& s, const CvWString& t) { return CvWString(s).append((const std::wstring&)t); }
inline CvWString operator+( const CvWString& s, const wchar* t) { return CvWString(s).append(t); }
inline CvWString operator+( const wchar* s, const CvWString& t) { return CvWString(s).append((const std::wstring&)t); }

class CvWStringBuffer
{
public:
	CvWStringBuffer() : m_pBuffer(NULL), m_iLength(0), m_iCapacity(0)
	{
	}

	~CvWStringBuffer()
	{
		SAFE_DELETE_ARRAY(m_pBuffer);
	}

	void append(wchar ch)
	{
		ensureCapacity(m_iLength + 2);
		m_pBuffer[m_iLength] = ch;
		m_pBuffer[++m_iLength] = 0; //null character
	}

	void append(const wchar *s, int len)
	{
		if(s && len > 0) {
			ensureCapacity(m_iLength + len + 1);
			memcpy(m_pBuffer + m_iLength, s, sizeof(wchar) * len); //append data (except null)
			m_iLength += len;
			m_pBuffer[m_iLength] = 0; //null character
		}
	}

	void append(const wchar *s)				{ append(s, s ? wcslen(s) : 0); }
	void append(const CvWString &s)			{ append(s.c_str(), s.length()); }
	void append(const std::wstring &s)		{ append(s.c_str(), s.length()); }
	void append(const CvWStringBuffer &buf)	{ append(buf.m_pBuffer, buf.m_iLength); }

	void append(const char *s)
	{
		if (s) {
			int len = MultiByteToWideChar(CP_ACP, MB_PRECOMPOSED, s, -1, NULL, 0);
			if (len > 1) /*include null*/
			{
				ensureCapacity(m_iLength + len);
				//append wchar data
				len = MultiByteToWideChar(CP_ACP, MB_PRECOMPOSED, s, -1, m_pBuffer + m_iLength, len);
				if(len > 1) {
					m_iLength += len - 1;
				}
			}
		}
	}

	bool appendfmt(const wchar * fmt, ...)
	{
		int len = 0;
		if(fmt) {
			va_list args;
			va_start(args, fmt);
			len = _vscwprintf(fmt, args);
			if(len > 0) {
				len += m_iLength + 1/*null*/;
				ensureCapacity(len);
				len = _vsnwprintf(m_pBuffer + m_iLength, m_iCapacity - len, fmt, args);
				if( len >= 0 )
					m_iLength += len;
				m_pBuffer[m_iLength] = 0; // confirm null terminate
			}
			va_end(args);
		}
		return (len >= 0);
	}

	void assign(const CvWString &s)		{ clear(); append(s.c_str(), s.length()); }
	void assign(const std::wstring &s)	{ clear(); append(s.c_str(), s.length()); }
	void assign(const wchar *s)			{ clear(); append(s); }
	void assign(const wchar *s, int len){ clear(); append(s, len); }

	void clear() {
		if(m_pBuffer) {
			m_pBuffer[m_iLength = 0] = 0; //null character
		}
	}

	void erase(size_t off = 0, size_t count = INT_MAX)
	{
		if(m_pBuffer) {
			if ((size_t)m_iLength <= off) return; // invalid offset
			if (m_iLength - off < count)
				count = m_iLength - off; // trim count
			if (0 < count)
			{	// move elements down
				::memcpy(m_pBuffer+off, m_pBuffer+off+count, (m_iLength - (off+count)) * sizeof(wchar));
				m_iLength -= count;
				m_pBuffer[m_iLength] = 0; // null terminate
			}
		}
	}

	bool isEmpty() const { return (m_iLength == 0); }

	const wchar *getCString()
	{
		ensureCapacity(1);
		return m_pBuffer;
	}

private:
	void ensureCapacity(int newCapacity)
	{
		if(newCapacity > m_iCapacity) _grow(newCapacity);
	}
	void _grow(int newCapacity);	// lol
	
	wchar *m_pBuffer;
	int m_iLength;
	int m_iCapacity;
};

//
// Wrapper std::string for C-string
// by lol
// 
// only purpose is passing C-string into std::string parameter
// only compatible msvc std::string impl.
// 
// @see FVariableSystem.h
//
class CvStaticString : public std::string
{
public:
	CvStaticString(const char* s) : std::string() { if(s) attach(s); }
	~CvStaticString() { detach(); }
private:
	void attach(const char *s)
	{
		_Myres	= _BUF_SIZE;
		_Mysize	= ::strlen(s);
		_Bx._Ptr= const_cast<char *>(s);
	}
	void detach () { _Myres = _Mysize = 0; }
	CvStaticString() { }
};

//
class CvString : public std::string
{
public:
	CvString() : std::string() {}
	CvString(int len)				: std::string( ) { reserve(len); }
	CvString(const char* s)			: std::string((s)?s:"") { } // lol: need to check NULL
	CvString(const std::string& s)	: std::string(s) { }
	CvString(const CvString& s)		: std::string((const std::string&)s) { }
	explicit CvString(const std::wstring& s) : std::string( ) { Copy(s.c_str()); } // don't want accidental conversions down to narrow strings
	~CvString() {}

	void Convert(const std::wstring& w) { Copy(w.c_str()); }
	void Copy(const wchar* w);

	// implicit conversion
	operator const char*() const { return c_str(); }

	// operators
	char& operator[](int i) { return std::string::operator[](i);	}
	char& operator[](std::string::size_type i) { return std::string::operator[](i);	}
	const char operator[](int i) const { return std::string::operator[](i);	}
	const CvString& operator=( const char* s) { if (s) assign(s); else clear();	return *this; }	
	const CvString& operator=( const std::string& s) { assign(s.c_str(), s.length()); return *this; }	

	// FString compatibility
	bool IsEmpty() const { return empty();	}
	const char* GetCString() const 	{ return c_str(); }							// convert
	int CompareNoCase( const char* lpsz ) const { return _stricmp(lpsz, c_str()); }
	int CompareNoCase( const char* lpsz, int iLength ) const { return _strnicmp(lpsz, c_str(), iLength);  }
	void Format( LPCSTR lpszFormat, ... );
	int GetLength() const { return size(); }
	int Replace( char chOld, char chNew );
	/************************************************************************************************/
	/* DEBUG_IS_MODULAR_ART                    05/12/08                                Faichele     */
	/*                                                                                              */
	/*                                                                                              */
	/************************************************************************************************/
	int Replace( const CvString& searchString, const CvString& replaceString);
	/************************************************************************************************/
	/* DEBUG_IS_MODULAR_ART                    END                                                  */
	/************************************************************************************************/

	void getTokens(const CvString& delimiters, std::vector<CvString>& tokensOut) const;

	CvString& appendSafe(const char* s) { if(s) append(s, ::strlen(s)); return *this; }

	// class format - MOD by lol
	class format;

	// static helpers
	static bool formatv(CvString& out, const char * fmt, va_list args);
	static int Replace(std::string& target, std::string const& search, std::string const& replace);
};

class CvString::format : public CvString
{
public:
	format(const char* fmt, ...) : CvString()
	{
		va_list args;
		va_start(args, fmt);
		formatv(*this, fmt, args);
		va_end(args);
	}
	~format() { };
private:
	format() { };
};

//////////////////////////////////////////////////////////////////////////
// INLINES
// Don't move these into a cpp file, since I don't want CvString to be part of the DLL, MT
//////////////////////////////////////////////////////////////////////////

inline int CvString::Replace( char chOld, char chNew )
{
	int nCount = 0;
	char *psz = const_cast<char *>(c_str());
	for(size_t n=length(); 0<n; --n, ++psz)
	{
		if (*psz == chOld)
		{
			*psz = chNew;
			++nCount;
		}
	}
	return nCount;
}


inline int CvString::Replace(std::string& target, std::string const& search, std::string const& replace)
{
	int nCount = 0;
	for(std::string::size_type pos = target.find(search);
		pos != std::string::npos;
		pos = target.find(search, pos) )
	{
		target.replace(pos, search.length(), replace);
		pos += search.length();
		++ nCount;
	}
	return nCount;
}

/************************************************************************************************/
/* DEBUG_IS_MODULAR_ART                    05/12/08                                Faichele     */
/*                                                                                              */
/*                                                                                              */
/************************************************************************************************/
inline int CvString::Replace(const CvString& searchString, const CvString& replaceString) 
{
	return Replace(*this, searchString, replaceString);
}
/************************************************************************************************/
/* DEBUG_IS_MODULAR_ART                    END                                                  */
/************************************************************************************************/

inline void CvString::getTokens(const CvString& delimiters, std::vector<CvString>& tokensOut) const
{
	//tokenizer code taken from http://www.digitalpeer.com/id/simple
	
	// skip delimiters at beginning.
	size_type lastPos = find_first_not_of(delimiters, 0);

	// find first "non-delimiter".
	size_type pos = find_first_of(delimiters, lastPos);

	while (CvString::npos != pos || CvString::npos != lastPos)
	{
		// found a token, parse it.
		tokensOut.push_back( substr(lastPos, pos - lastPos) );
		
		// skip delimiters.  Note the "not_of"
		lastPos = find_first_not_of(delimiters, pos);

		// find next "non-delimiter"
		pos = find_first_of(delimiters, lastPos);
	}
}

inline void CvWString::Format( LPCWSTR lpszFormat, ... )
{
	va_list args;
	va_start(args,lpszFormat);
	formatv(*this,lpszFormat,args);
	va_end(args);
}

inline void CvWString::AppendFormat( LPCWSTR lpszFormat, ... )
{
	va_list args;
	va_start(args,lpszFormat);
	appendfmtv(*this,lpszFormat,args);
	va_end(args);
}

inline void CvString::Format( LPCSTR lpszFormat, ... )
{
	va_list args;
	va_start(args,lpszFormat);
	formatv(*this,lpszFormat,args);
	va_end(args);
}

extern const CvString  EmptySS; // ""
extern const CvString  CommaSS; // ","
extern const CvWString EmptyWS; // L""
extern const CvWString CommaWS; // L", "
extern const CvWString DelimWS; // L": "

#define StrFormatA CvString::format
#define StrFormatW CvWString::format

//#pragma warning( pop )

#endif	// CvString_h