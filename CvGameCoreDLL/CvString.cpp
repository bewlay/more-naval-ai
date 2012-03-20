#include "CvGameCoreDLL.h"


const CvString  EmptySS("");
const CvString  CommaSS(",");
const CvWString EmptyWS(L"");
const CvWString CommaWS(L", ");
const CvWString DelimWS(L": ");

//
// CvString
//

void CvString::Copy(const wchar* w)
{
	if (w) {
		int len = WideCharToMultiByte(CP_ACP, 0, w, -1, NULL, 0, NULL, NULL);
		if (len)
		{
			reserve(len-1);
			len = WideCharToMultiByte(CP_ACP, 0, w, -1, const_cast<char *>(c_str()), len, NULL, NULL);
			_Eos((len==0) ? 0 : (len-1));
		}
	}
}

void CvWString::Copy(const char* s)
{
	if (s) {
		int len = MultiByteToWideChar(CP_ACP, MB_PRECOMPOSED, s, -1, NULL, 0);
		if (len)
		{
			reserve(len-1);
			len = MultiByteToWideChar(CP_ACP, MB_PRECOMPOSED, s, -1, const_cast<wchar *>(c_str()), len);
			_Eos((len==0) ? 0 : (len-1));
		}
	}
}

//
// static
//
bool CvString::formatv(CvString& out, const char * fmt, va_list args)
{
	int len = 0;
	if(fmt) {
		char buf[2048];
		len = _vsnprintf(buf, 2048, fmt, args);
		if(len >= 0)
		{
			out.assign(buf, len);
			return true;
		}
		else
		{
			size_t maxlength = (out.capacity() > 4097) ? out.capacity() : 4097;
			out._Eos(0);
			do
			{
				out.reserve(maxlength);
				len = _vsnprintf(const_cast<char *>( out.c_str() ), out.capacity(), fmt, args);
				if (len >= 0) // If that worked, return the string.
				{
					out._Eos(len);
					break;
				}
				if(maxlength >= 81919) // 81920 == 80K limit
				{
					out.erase();
					break;
				}
				// twice the old size
				maxlength += out.capacity() + 1;
			} while(true);
		}
	}
	else
		out.erase();
	return (len >= 0);
}

//
// static
//
bool CvWString::formatv(CvWString& out, const wchar * fmt, va_list args)
{
	int len = 0;
	if(fmt) {
		wchar buf[2048];
		len = _vsnwprintf(buf, 2048, fmt, args);
		if(len >= 0)
		{
			out.assign(buf, len);
			return true;
		}
		else
		{
			size_t maxlength = (out.capacity() > 4097) ? out.capacity() : 4097;
			out._Eos(0);
			do
			{
				out.reserve(maxlength);
				len = _vsnwprintf(const_cast<wchar *>( out.c_str() ), out.capacity(), fmt, args);
				if (len >= 0) // If that worked, return the string.
				{
					out._Eos(len);
					break;
				}
				if(maxlength >= 81919) // 81920 == 80K limit
				{
					out.erase();
					break;
				}
				// twice the old size
				maxlength += out.capacity() + 1;
			} while(true);
		}
	}
	else
		out.erase();
	return (len >= 0);
}

//
// static
//
bool CvWString::appendfmtv(CvWString& out, const wchar * fmt, va_list args)
{
	int len = 0;
	if(fmt) {
		len = _vscwprintf(fmt, args);
		if(len > 0) {
			out.reserve(out.length() + len);
			len = _vsnwprintf(const_cast<wchar *>( out.c_str() ) + out.length(), out.capacity()-out.length(), fmt, args);
			if( len >= 0 )
				out._Eos(out.length() + len);
		}
	}
	return (len >= 0);
}

void CvWStringBuffer::_grow(int newCapacity)
{
	m_iCapacity = 2 * newCapacity; //grow by %100

	wchar *newBuffer = new wchar [m_iCapacity];
	
	//copy data
	if(m_pBuffer)
	{
		memcpy(newBuffer, m_pBuffer, sizeof(wchar) * (m_iLength + 1/*NULL*/));
		//erase old memory
		delete [] m_pBuffer;
	}
	else
	{
		newBuffer[0] = 0; //null character
	}
	m_pBuffer = newBuffer;		
}
