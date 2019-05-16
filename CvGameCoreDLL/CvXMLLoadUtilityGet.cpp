//
// XML Get functions
//

#include "CvGameCoreDLL.h"
#include "CvDLLXMLIFaceBase.h"
#include "CvXMLLoadUtility.h"
#include "CvGlobals.h"
#include "CvArtFileMgr.h"
#include "FInputDevice.h"
#include "FProfiler.h"

//
// STATIC
// for progress bar display
// returns the number of steps we use
//
int CvXMLLoadUtility::GetNumProgressSteps()
{
	return 20;	// the function UpdateProgressCB() is called 20 times by CvXMLLoadUtilitySet
}

// Helper functions

// Get the value from the last located node. Returns true if successful.
// Otherwise, get default value, show assert and return false.
// These functions specifically check if the node is empty for non-string values.

bool SafeGetLastNodeValue( FXml* xml, std::string& pszVal, char* pszDefault ) {
	bool success = gDLL->getXMLIFace()->GetLastNodeValue( xml, pszVal );
	if( success ) {
		return true;
	}
	else {
		FAssertMsg( false, "Error getting value, probably not a string" );
		if( pszDefault ) {
			pszVal = pszDefault;
		}
		else {
			pszVal.clear();
		}
		return false;
	}
}

bool SafeGetLastNodeValue( FXml* xml, std::wstring& pszVal, wchar* pszDefault )  {
	bool success = gDLL->getXMLIFace()->GetLastNodeValue( xml, pszVal );
	if( success ) {
		return true;
	}
	else {
		FAssertMsg( false, "Error getting value, probably not a wstring" );
		if( pszDefault ) {
			pszVal = pszDefault;
		}
		else {
			pszVal.clear();
		}
		return false;
	}
}

bool SafeGetLastNodeValue( FXml* xml, bool* pbVal, bool bDefault ) {
	// Check whether node is empty
	if( gDLL->getXMLIFace()->GetLastNodeTextSize( xml ) == 0 ) {
		FAssertMsg( false, "Error getting bool, empty element" );
		*pbVal = bDefault;
		return false;
	}

	bool success = gDLL->getXMLIFace()->GetLastNodeValue( xml, pbVal );
	if( success ) {
		return true;
	}
	else {
		FAssertMsg( false, "Error getting value" );
		*pbVal = bDefault;
		return false;
	}
}

bool SafeGetLastNodeValue( FXml* xml, int* piVal, int iDefault ) {
	// Check whether node is empty
	if( gDLL->getXMLIFace()->GetLastNodeTextSize( xml ) == 0 ) {
		FAssertMsg( false, "Error getting int, empty element" );
		*piVal = iDefault;
		return false;
	}

	bool success = gDLL->getXMLIFace()->GetLastNodeValue( xml, piVal );
	if( success ) {
		return true;
	}
	else {
		FAssertMsg( false, "Error getting value" );
		*piVal = iDefault;
		return false;
	}
}

bool SafeGetLastNodeValue( FXml* xml, float* pfVal, float fDefault ) {
	// Check whether node is empty
	if( gDLL->getXMLIFace()->GetLastNodeTextSize( xml ) == 0 ) {
		FAssertMsg( false, "Error getting float, empty element" );
		*pfVal = fDefault;
		return false;
	}

	bool success = gDLL->getXMLIFace()->GetLastNodeValue( xml, pfVal );
	if( success ) {
		return true;
	}
	else {
		FAssertMsg( false, "Error getting value" );
		*pfVal = fDefault;
		return false;
	}
}

bool SafeGetLastNodeValue( FXml* xml, unsigned int* puiVal, unsigned int uiDefault ) {
	// Check whether node is empty
	if( gDLL->getXMLIFace()->GetLastNodeTextSize( xml ) == 0 ) {
		FAssertMsg( false, "Error getting uint, empty element" );
		*puiVal = uiDefault;
		return false;
	}

	bool success = gDLL->getXMLIFace()->GetLastNodeValue( xml, puiVal );
	if( success ) {
		return true;
	}
	else {
		FAssertMsg( false, "Error getting value" );
		*puiVal = uiDefault;
		return false;
	}
}


//------------------------------------------------------------------------------------------------------
//
//  FUNCTION:   GetXmlVal(char* pszVal, char* pszDefault = NULL)
//
//  PURPOSE :   Get the string value of the current xml node or the next non-comment xml node if the
//				current node is a comment node
//
//------------------------------------------------------------------------------------------------------
bool CvXMLLoadUtility::GetXmlVal(char* pszVal, char* pszDefault)
{
	if (pszDefault)
	{
		strcpy(pszVal, pszDefault);
	}
	else
	{
		strcpy(pszVal, "");
	}

	// skip to the next non-comment node
	if (SkipToNextVal())
	{
		// get the string value of the current xml node
		gDLL->getXMLIFace()->GetLastNodeValue(m_pFXml,pszVal);
		return true;
	}
	// otherwise we can't find a non-comment node on this level so we will FAssert and return false
	else
	{
		FAssertMsg(false , "Error in GetXmlVal function, unable to find the next non-comment node");
		return false;
	}
}

//------------------------------------------------------------------------------------------------------
//
//  FUNCTION:   GetXmlVal(wchar* pszVal, wchar* pszDefault = NULL)
//
//  PURPOSE :   Get the string value of the current xml node or the next non-comment xml node if the
//				current node is a comment node
//
//------------------------------------------------------------------------------------------------------
bool CvXMLLoadUtility::GetXmlVal(wchar* pszVal, wchar* pszDefault)
{
	if (pszDefault)
	{
		wcscpy(pszVal, pszDefault);
	}
	else
	{
		wcscpy(pszVal, L"");
	}

	// skip to the next non-comment node
	if (SkipToNextVal())
	{
		// get the string value of the current xml node
		gDLL->getXMLIFace()->GetLastNodeValue(m_pFXml,pszVal);
		return true;
	}
	// otherwise we can't find a non-comment node on this level so we will FAssert and return false
	else
	{
		FAssertMsg(false , "Error in GetXmlVal function, unable to find the next non-comment node");
		return false;
	}
}

//------------------------------------------------------------------------------------------------------
//
//  FUNCTION:   GetXmlVal(std::string& pszVal, char* pszDefault = NULL)
//
//  PURPOSE :   Get the string value of the current xml node or the next non-comment xml node if the
//				current node is a comment node
//
//------------------------------------------------------------------------------------------------------
bool CvXMLLoadUtility::GetXmlVal(std::string& pszVal, char* pszDefault)
{
	if (pszDefault)
	{
		pszVal = pszDefault;
	}
	else
	{
		pszVal.clear();
	}

	// skip to the next non-comment node
	if (SkipToNextVal())
	{
		// get the string value of the current xml node
		return SafeGetLastNodeValue(m_pFXml,pszVal,pszDefault);
	}
	// otherwise we can't find a non-comment node on this level so we will FAssert and return false
	else
	{
		FAssertMsg(false , "Error in GetXmlVal function, unable to find the next non-comment node");
		return false;
	}
}


//------------------------------------------------------------------------------------------------------
//
//  FUNCTION:   GetXmlVal(std::wstring& pszVal, wchar* pszDefault = NULL)
//
//  PURPOSE :   Get the string value of the current xml node or the next non-comment xml node if the
//				current node is a comment node
//
//------------------------------------------------------------------------------------------------------
bool CvXMLLoadUtility::GetXmlVal(std::wstring& pszVal, wchar* pszDefault)
{
	if (pszDefault)
	{
		pszVal = pszDefault;
	}
	else
	{
		pszVal.clear();
	}

	// skip to the next non-comment node
	if (SkipToNextVal())
	{
		// get the string value of the current xml node
		return SafeGetLastNodeValue(m_pFXml,pszVal,pszDefault);
	}
	// otherwise we can't find a non-comment node on this level so we will FAssert and return false
	else
	{
		FAssertMsg(false , "Error in GetXmlVal function, unable to find the next non-comment node");
		return false;
	}
}

//------------------------------------------------------------------------------------------------------
//
//  FUNCTION:   GetXmlVal(int* piVal, int iDefault = 0)
//
//  PURPOSE :   Get the int value of the current xml node or the next non-comment xml node if the
//				current node is a comment node
//
//------------------------------------------------------------------------------------------------------
bool CvXMLLoadUtility::GetXmlVal(int* piVal, int iDefault)
{
	// set the value to the default
	*piVal = iDefault;

	// skip to the next non-comment node
	if (SkipToNextVal())
	{
		// get the string value of the current xml node
		return SafeGetLastNodeValue(m_pFXml,piVal,iDefault);
	}
	// otherwise we can't find a non-comment node on this level so we will FAssert and return false
	else
	{
		FAssertMsg(false , "Error in GetXmlVal function, unable to find the next non-comment node");
		return false;
	}
}

//------------------------------------------------------------------------------------------------------
//
//  FUNCTION:   GetXmlVal(float* pfVal, float fDefault = 0.0f)
//
//  PURPOSE :   Get the float value of the current xml node or the next non-comment xml node if the
//				current node is a comment node
//
//------------------------------------------------------------------------------------------------------
bool CvXMLLoadUtility::GetXmlVal(float* pfVal, float fDefault)
{
	// set the value to the default
	*pfVal = fDefault;

	// skip to the next non-comment node
	if (SkipToNextVal())
	{
		// get the string value of the current xml node
		return SafeGetLastNodeValue(m_pFXml,pfVal,fDefault);
	}
	// otherwise we can't find a non-comment node on this level so we will FAssert and return false
	else
	{
		FAssertMsg(false , "Error in GetXmlVal function, unable to find the next non-comment node");
		return false;
	}
}

//------------------------------------------------------------------------------------------------------
//
//  FUNCTION:   GetXmlVal(bool* pbVal, bool bDefault = false)
//
//  PURPOSE :   Get the boolean value of the current xml node or the next non-comment xml node if the
//				current node is a comment node
//
//------------------------------------------------------------------------------------------------------
bool CvXMLLoadUtility::GetXmlVal(bool* pbVal, bool bDefault)
{
	// set the boolean value to it's default value
	*pbVal = bDefault;

	// skip to the next non-comment node
	if (SkipToNextVal())
	{
		// get the string value of the current xml node
		return SafeGetLastNodeValue(m_pFXml,pbVal,bDefault);
	}
	// otherwise we can't find a non-comment node on this level so we will FAssert and return false
	else
	{
		FAssertMsg(false , "Error in GetXmlVal function, unable to find the next non-comment node");
		return false;
	}
}


//------------------------------------------------------------------------------------------------------
//
//  FUNCTION:   GetNextXmlVal(std::string& pszVal, char* pszDefault = NULL)
//
//  PURPOSE :   Get the string value of the next sibling of the current xml node or the next 
//				non-comment xml node if the current node is a comment node
//
//------------------------------------------------------------------------------------------------------
bool CvXMLLoadUtility::GetNextXmlVal(std::string& pszVal, char* pszDefault)
{
	if (pszDefault)
	{
		pszVal = pszDefault;
	}
	else
	{
		pszVal.clear();
	}

	// if we can set the current xml node to it's next sibling
	if (gDLL->getXMLIFace()->NextSibling(m_pFXml))
	{
		// skip to the next non-comment node
		if (SkipToNextVal())
		{
			// get the string value of the current xml node
			return SafeGetLastNodeValue(m_pFXml,pszVal,pszDefault);
		}
		// otherwise we can't find a non-comment node on this level so we will FAssert and return false
		else
		{
			FAssertMsg(false , "Error in GetNextXmlVal function, unable to find the next non-comment node");
			return false;
		}
	}
	// otherwise there are no more sibling nodes but we were expecting them so FAssert and return false
	else
	{
		return false;
	}
}

//------------------------------------------------------------------------------------------------------
//
//  FUNCTION:   GetNextXmlVal(std::wstring& pszVal, wchar* pszDefault = NULL)
//
//  PURPOSE :   Get the string value of the next sibling of the current xml node or the next 
//				non-comment xml node if the current node is a comment node
//
//------------------------------------------------------------------------------------------------------
bool CvXMLLoadUtility::GetNextXmlVal(std::wstring& pszVal, wchar* pszDefault)
{
	if (pszDefault)
	{
		pszVal = pszDefault;
	}
	else
	{
		pszVal.clear();
	}

	// if we can set the current xml node to it's next sibling
	if (gDLL->getXMLIFace()->NextSibling(m_pFXml))
	{
		// skip to the next non-comment node
		if (SkipToNextVal())
		{
			// get the string value of the current xml node
			return SafeGetLastNodeValue(m_pFXml,pszVal,pszDefault);
		}
		// otherwise we can't find a non-comment node on this level so we will FAssert and return false
		else
		{
			FAssertMsg(false , "Error in GetNextXmlVal function, unable to find the next non-comment node");
			return false;
		}
	}
	// otherwise there are no more sibling nodes but we were expecting them so FAssert and return false
	else
	{
		return false;
	}
}

//------------------------------------------------------------------------------------------------------
//
//  FUNCTION:   GetNextXmlVal(char* pszVal, char* pszDefault = NULL)
//
//  PURPOSE :   Get the string value of the next sibling of the current xml node or the next 
//				non-comment xml node if the current node is a comment node
//
//------------------------------------------------------------------------------------------------------
bool CvXMLLoadUtility::GetNextXmlVal(char* pszVal, char* pszDefault)
{
	if (pszDefault)
	{
		strcpy(pszVal, pszDefault);
	}
	else
	{
		strcpy(pszVal, "");
	}

	// if we can set the current xml node to it's next sibling
	if (gDLL->getXMLIFace()->NextSibling(m_pFXml))
	{
		// skip to the next non-comment node
		if (SkipToNextVal())
		{
			// get the string value of the current xml node
			gDLL->getXMLIFace()->GetLastNodeValue(m_pFXml,pszVal);
			return true;
		}
		// otherwise we can't find a non-comment node on this level so we will FAssert and return false
		else
		{
			FAssertMsg(false , "Error in GetNextXmlVal function, unable to find the next non-comment node");
			return false;
		}
	}
	// otherwise there are no more sibling nodes but we were expecting them so FAssert and return false
	else
	{
		return false;
	}
}

//------------------------------------------------------------------------------------------------------
//
//  FUNCTION:   GetNextXmlVal(wchar* pszVal, wchar* pszDefault = NULL)
//
//  PURPOSE :   Get the string value of the next sibling of the current xml node or the next 
//				non-comment xml node if the current node is a comment node
//
//------------------------------------------------------------------------------------------------------
bool CvXMLLoadUtility::GetNextXmlVal(wchar* pszVal, wchar* pszDefault)
{
	if (pszDefault)
	{
		wcscpy(pszVal, pszDefault);
	}
	else
	{
		wcscpy(pszVal, L"");
	}

	// if we can set the current xml node to it's next sibling
	if (gDLL->getXMLIFace()->NextSibling(m_pFXml))
	{
		// skip to the next non-comment node
		if (SkipToNextVal())
		{
			// get the string value of the current xml node
			gDLL->getXMLIFace()->GetLastNodeValue(m_pFXml,pszVal);
			return true;
		}
		// otherwise we can't find a non-comment node on this level so we will FAssert and return false
		else
		{
			FAssertMsg(false , "Error in GetNextXmlVal function, unable to find the next non-comment node");
			return false;
		}
	}
	// otherwise there are no more sibling nodes but we were expecting them so FAssert and return false
	else
	{
		return false;
	}
}

//------------------------------------------------------------------------------------------------------
//
//  FUNCTION:   GetNextXmlVal(int* piVal, int iDefault = 0)
//
//  PURPOSE :   Get the int value of the next sibling of the current xml node or the next
//				non-comment xml node if the current node is a comment node
//
//------------------------------------------------------------------------------------------------------
bool CvXMLLoadUtility::GetNextXmlVal(int* piVal, int iDefault)
{
	// set the value to the default
	*piVal = iDefault;

	// if we can set the current xml node to it's next sibling
	if (gDLL->getXMLIFace()->NextSibling(m_pFXml))
	{
		// skip to the next non-comment node
		if (SkipToNextVal())
		{
			// get the string value of the current xml node
			return SafeGetLastNodeValue(m_pFXml,piVal, iDefault);
		}
		// otherwise we can't find a non-comment node on this level so we will FAssert and return false
		else
		{
			FAssertMsg(false , "Error in GetNextXmlVal function, unable to find the next non-comment node");
			return false;
		}
	}
	// otherwise there are no more sibling nodes but we were expecting them so FAssert and return false
	else
	{
		return false;
	}
}

//------------------------------------------------------------------------------------------------------
//
//  FUNCTION:   GetNextXmlVal(float* pfVal, float fDefault = 0.0f)
//
//  PURPOSE :   Get the float value of the next sibling of the current xml node or the next
//				non-comment xml node if the current node is a comment node
//
//------------------------------------------------------------------------------------------------------
bool CvXMLLoadUtility::GetNextXmlVal(float* pfVal, float fDefault)
{
	// set the value to the default
	*pfVal = fDefault;

	// if we can set the current xml node to it's next sibling
	if (gDLL->getXMLIFace()->NextSibling(m_pFXml))
	{
		// skip to the next non-comment node
		if (SkipToNextVal())
		{
			// get the string value of the current xml node
			return SafeGetLastNodeValue(m_pFXml,pfVal, fDefault);
		}
		// otherwise we can't find a non-comment node on this level so we will FAssert and return false
		else
		{
			FAssertMsg(false , "Error in GetNextXmlVal function, unable to find the next non-comment node");
			return false;
		}
	}
	// otherwise there are no more sibling nodes but we were expecting them so FAssert and return false
	else
	{
		return false;
	}
}

//------------------------------------------------------------------------------------------------------
//
//  FUNCTION:   GetNextXmlVal(bool* pbVal, bool bDefault = false)
//
//  PURPOSE :   Get the boolean value of the next sibling of the current xml node or the next
//				non-comment xml node if the current node is a comment node
//
//------------------------------------------------------------------------------------------------------
bool CvXMLLoadUtility::GetNextXmlVal(bool* pbVal, bool bDefault)
{
	// set the boolean value to it's default value
	*pbVal = bDefault;

	// if we can set the current xml node to it's next sibling
	if (gDLL->getXMLIFace()->NextSibling(m_pFXml))
	{
		// skip to the next non-comment node
		if (SkipToNextVal())
		{
			// get the string value of the current xml node
			return SafeGetLastNodeValue(m_pFXml,pbVal,bDefault);
		}
		// otherwise we can't find a non-comment node on this level so we will FAssert and return false
		else
		{
			FAssertMsg(false , "Error in GetNextXmlVal function, unable to find the next non-comment node");
			return false;
		}
	}
	// otherwise there are no more sibling nodes but we were expecting them so FAssert and return false
	else
	{
		return false;
	}
}

//------------------------------------------------------------------------------------------------------
//
//  FUNCTION:   GetChildXmlVal(std::string& pszVal, char* pszDefault = NULL)
//
//  PURPOSE :   overloaded function that sets the current xml node to it's first non-comment child node 
//				and then that node's string value
//
//------------------------------------------------------------------------------------------------------
bool CvXMLLoadUtility::GetChildXmlVal(std::string& pszVal, char* pszDefault)
{
	if (pszDefault)
	{
		pszVal = pszDefault;
	}
	else
	{
		pszVal.clear();
	}

	// if we successfully set the current xml node to it's first child node
	if (gDLL->getXMLIFace()->SetToChild(m_pFXml))
	{
		// skip to the next non-comment node
		if (SkipToNextVal())
		{
			// get the string value of the current xml node
			return SafeGetLastNodeValue(m_pFXml,pszVal,pszDefault);
		}
		// otherwise we can't find a non-comment node on this level so we will FAssert and return false
		else
		{
			FAssertMsg(false , "Error in GetChildXmlVal function, unable to find the next non-comment node");
			return false;
		}
	}
	// otherwise there are no child nodes but we were expecting them so FAssert and return false
	else
	{
		FAssertMsg(false , "Error in GetChildXmlVal function, unable to find a child node");
		return false;
	}
}

//------------------------------------------------------------------------------------------------------
//
//  FUNCTION:   GetChildXmlVal(std::wstring& pszVal, wchar* pszDefault = NULL)
//
//  PURPOSE :   overloaded function that sets the current xml node to it's first non-comment child node 
//				and then that node's string value
//
//------------------------------------------------------------------------------------------------------
bool CvXMLLoadUtility::GetChildXmlVal(std::wstring& pszVal, wchar* pszDefault)
{
	if (pszDefault)
	{
		pszVal = pszDefault;
	}
	else
	{
		pszVal.clear();
	}

	// if we successfully set the current xml node to it's first child node
	if (gDLL->getXMLIFace()->SetToChild(m_pFXml))
	{
		// skip to the next non-comment node
		if (SkipToNextVal())
		{
			// get the string value of the current xml node
			return SafeGetLastNodeValue(m_pFXml,pszVal,pszDefault);
		}
		// otherwise we can't find a non-comment node on this level so we will FAssert and return false
		else
		{
			FAssertMsg(false , "Error in GetChildXmlVal function, unable to find the next non-comment node");
			return false;
		}
	}
	// otherwise there are no child nodes but we were expecting them so FAssert and return false
	else
	{
		FAssertMsg(false , "Error in GetChildXmlVal function, unable to find a child node");
		return false;
	}
}


//------------------------------------------------------------------------------------------------------
//
//  FUNCTION:   GetChildXmlVal(char* pszVal, char* pszDefault = NULL)
//
//  PURPOSE :   overloaded function that sets the current xml node to it's first non-comment child node 
//				and then that node's string value
//
//------------------------------------------------------------------------------------------------------
bool CvXMLLoadUtility::GetChildXmlVal(char* pszVal, char* pszDefault)
{
	if (pszDefault)
	{
		strcpy(pszVal, pszDefault);
	}
	else
	{
		strcpy(pszVal, "");
	}

	// if we successfully set the current xml node to it's first child node
	if (gDLL->getXMLIFace()->SetToChild(m_pFXml))
	{
		// skip to the next non-comment node
		if (SkipToNextVal())
		{
			// get the string value of the current xml node
			gDLL->getXMLIFace()->GetLastNodeValue(m_pFXml,pszVal);
			return true;
		}
		// otherwise we can't find a non-comment node on this level so we will FAssert and return false
		else
		{
			FAssertMsg(false , "Error in GetChildXmlVal function, unable to find the next non-comment node");
			return false;
		}
	}
	// otherwise there are no child nodes but we were expecting them so FAssert and return false
	else
	{
		FAssertMsg(false , "Error in GetChildXmlVal function, unable to find a child node");
		return false;
	}
}

//------------------------------------------------------------------------------------------------------
//
//  FUNCTION:   GetChildXmlVal(wchar* pszVal, wchar* pszDefault = NULL)
//
//  PURPOSE :   overloaded function that sets the current xml node to it's first non-comment child node 
//				and then that node's string value
//
//------------------------------------------------------------------------------------------------------
bool CvXMLLoadUtility::GetChildXmlVal(wchar* pszVal, wchar* pszDefault)
{
	if (pszDefault)
	{
		wcscpy(pszVal, pszDefault);
	}
	else
	{
		wcscpy(pszVal, L"");
	}

	// if we successfully set the current xml node to it's first child node
	if (gDLL->getXMLIFace()->SetToChild(m_pFXml))
	{
		// skip to the next non-comment node
		if (SkipToNextVal())
		{
			// get the string value of the current xml node
			gDLL->getXMLIFace()->GetLastNodeValue(m_pFXml,pszVal);
			return true;
		}
		// otherwise we can't find a non-comment node on this level so we will FAssert and return false
		else
		{
			FAssertMsg(false , "Error in GetChildXmlVal function, unable to find the next non-comment node");
			return false;
		}
	}
	// otherwise there are no child nodes but we were expecting them so FAssert and return false
	else
	{
		FAssertMsg(false , "Error in GetChildXmlVal function, unable to find a child node");
		return false;
	}
}

//------------------------------------------------------------------------------------------------------
//
//  FUNCTION:   GetChildXmlVal(int* piVal, int iDefault = 0)
//
//  PURPOSE :   overloaded function that sets the current xml node to it's first non-comment child node 
//				and then that node's integer value
//
//------------------------------------------------------------------------------------------------------
bool CvXMLLoadUtility::GetChildXmlVal(int* piVal, int iDefault)
{
	// set the value to the default
	*piVal = iDefault;

	// if we successfully set the current xml node to it's first child node
	if (gDLL->getXMLIFace()->SetToChild(m_pFXml))
	{
		// skip to the next non-comment node
		if (SkipToNextVal())
		{
			// get the string value of the current xml node
			return SafeGetLastNodeValue(m_pFXml,piVal,iDefault);
		}
		// otherwise we can't find a non-comment node on this level so we will FAssert and return false
		else
		{
			FAssertMsg(false , "Error in GetChildXmlVal function, unable to find the next non-comment node");
			return false;
		}
	}
	// otherwise there are no child nodes but we were expecting them so FAssert and return false
	else
	{
		FAssertMsg(false , "Error in GetChildXmlVal function, unable to find a child node");
		return false;
	}
}

//------------------------------------------------------------------------------------------------------
//
//  FUNCTION:   GetChildXmlVal(float* pfVal, float fDefault = 0.0f)
//
//  PURPOSE :   overloaded function that sets the current xml node to it's first non-comment child node 
//				and then that node's float value
//
//------------------------------------------------------------------------------------------------------
bool CvXMLLoadUtility::GetChildXmlVal(float* pfVal, float fDefault)
{
	// set the value to the default
	*pfVal = fDefault;

	// if we successfully set the current xml node to it's first child node
	if (gDLL->getXMLIFace()->SetToChild(m_pFXml))
	{
		// skip to the next non-comment node
		if (SkipToNextVal())
		{
			// get the string value of the current xml node
			return SafeGetLastNodeValue(m_pFXml,pfVal,fDefault);
		}
		// otherwise we can't find a non-comment node on this level so we will FAssert and return false
		else
		{
			FAssertMsg(false, "Error in GetChildXmlVal function, unable to find the next non-comment node");
			return false;
		}
	}
	// otherwise there are no child nodes but we were expecting them so FAssert and return false
	else
	{
		FAssertMsg(false, "Error in GetChildXmlVal function, unable to find a child node");
		return false;
	}
}

//------------------------------------------------------------------------------------------------------
//
//  FUNCTION:   GetChildXmlVal(bool* pbVal, bool bDefault = false)
//
//  PURPOSE :   overloaded function that sets the current xml node to it's first non-comment child node 
//				and then that node's boolean value
//
//------------------------------------------------------------------------------------------------------
bool CvXMLLoadUtility::GetChildXmlVal(bool* pbVal, bool bDefault)
{
	// set the boolean value to it's default value
	*pbVal = bDefault;

	// if we successfully set the current xml node to it's first child node
	if (gDLL->getXMLIFace()->SetToChild(m_pFXml))
	{
		// skip to the next non-comment node
		if (SkipToNextVal())
		{
			// get the string value of the current xml node
			return SafeGetLastNodeValue(m_pFXml,pbVal,bDefault);
		}
		// otherwise we can't find a non-comment node on this level so we will FAssert and return false
		else
		{
			FAssertMsg(false, "Error in GetChildXmlVal function, unable to find the next non-comment node");
			return false;
		}
	}
	// otherwise there are no child nodes but we were expecting them so FAssert and return false
	else
	{
		FAssertMsg(false, "Error in GetChildXmlVal function, unable to find a child node");
		return false;
	}
}

//------------------------------------------------------------------------------------------------------
//
//  FUNCTION:   GetChildXmlValByName(wchar* pszVal, const TCHAR* szName, TCHAR* pszDefault = NULL)
//
//  PURPOSE :   Overloaded function that gets the child value of the tag with szName if there is only one child
// 				value of that name

//
//------------------------------------------------------------------------------------------------------
bool CvXMLLoadUtility::GetChildXmlValByName(wchar* pszVal, const TCHAR* szName, wchar* pszDefault)
{
	int iNumChildrenByTagName=1;

	if (pszDefault)
	{
		wcscpy(pszVal, pszDefault);
	}
	else
	{
		wcscpy(pszVal, L"");
	}

#if 0
	iNumChildrenByTagName = gDLL->getXMLIFace()->NumOfChildrenByTagName(m_pFXml,szName);
	FAssertMsg((iNumChildrenByTagName < 2),"More children with tag name than expected, should only be 1.");
#endif
	// we only continue if there are one and only one children with this tag name
	if (iNumChildrenByTagName == 1)
	{
		if (gDLL->getXMLIFace()->SetToChildByTagName(m_pFXml,szName))
		{
			// skip to the next non-comment node
			if (SkipToNextVal())
			{
				// get the string value of the current xml node
				bool success = gDLL->getXMLIFace()->GetLastNodeValue(m_pFXml,pszVal);
				gDLL->getXMLIFace()->SetToParent(m_pFXml);
				return success;
			}
			// otherwise we can't find a non-comment node on this level so we will FAssert and return false
			else
			{
				FAssertMsg(false, "Error in GetChildXmlValByName function, unable to find the next non-comment node");
				gDLL->getXMLIFace()->SetToParent(m_pFXml);
				return false;
			}
		}
		// otherwise there are no child nodes but we were expecting them so FAssert and return false
		else
		{
//			FAssertMsg(false, "Error in GetChildXmlValByName function, unable to find a specified node");
			return false;
		}
	}
	else
	{
		// FAssertMsg(false, "Error in GetChildXmlValByName function, unable to find a specified node");
		return false;
	}
}

//------------------------------------------------------------------------------------------------------
//
//  FUNCTION:   GetChildXmlValByName(char* pszVal, const TCHAR* szName, TCHAR* pszDefault = NULL)
//
//  PURPOSE :   Overloaded function that gets the child value of the tag with szName if there is only one child
// 				value of that name

//
//------------------------------------------------------------------------------------------------------
bool CvXMLLoadUtility::GetChildXmlValByName(char* pszVal, const TCHAR* szName, char* pszDefault)
{
	int iNumChildrenByTagName=1;

	if (pszDefault)
	{
		strcpy(pszVal, pszDefault);
	}
	else
	{
		strcpy(pszVal, "");
	}

#if 0
	iNumChildrenByTagName = gDLL->getXMLIFace()->NumOfChildrenByTagName(m_pFXml,szName);
	FAssertMsg((iNumChildrenByTagName < 2),"More children with tag name than expected, should only be 1.");
#endif
	// we only continue if there are one and only one children with this tag name
	if (iNumChildrenByTagName == 1)
	{
		if (gDLL->getXMLIFace()->SetToChildByTagName(m_pFXml,szName))
		{
			// skip to the next non-comment node
			if (SkipToNextVal())
			{
				// get the string value of the current xml node
				bool success = gDLL->getXMLIFace()->GetLastNodeValue(m_pFXml,pszVal);
				gDLL->getXMLIFace()->SetToParent(m_pFXml);
				return success;
			}
			// otherwise we can't find a non-comment node on this level so we will FAssert and return false
			else
			{
				FAssertMsg(false, "Error in GetChildXmlValByName function, unable to find the next non-comment node");
				gDLL->getXMLIFace()->SetToParent(m_pFXml);
				return false;
			}
		}
		// otherwise there are no child nodes but we were expecting them so FAssert and return false
		else
		{
//			FAssertMsg(false, "Error in GetChildXmlValByName function, unable to find a specified node");
			return false;
		}
	}
	else
	{
		// FAssertMsg(false, "Error in GetChildXmlValByName function, unable to find a specified node");
		return false;
	}
}


//------------------------------------------------------------------------------------------------------
//
//  FUNCTION:   GetChildXmlValByName(std::string& pszVal, const TCHAR* szName, TCHAR* pszDefault = NULL)
//
//  PURPOSE :   Overloaded function that gets the child value of the tag with szName if there is only one child
// 				value of that name

//
//------------------------------------------------------------------------------------------------------
bool CvXMLLoadUtility::GetChildXmlValByName(std::string& pszVal, const TCHAR* szName, char* pszDefault)
{
	int iNumChildrenByTagName=1;

	if (pszDefault)
	{
		pszVal=pszDefault;
	}
	else
	{
		pszVal.clear();
	}

#if 0
	iNumChildrenByTagName = gDLL->getXMLIFace()->NumOfChildrenByTagName(m_pFXml,szName);
	FAssertMsg((iNumChildrenByTagName < 2),"More children with tag name than expected, should only be 1.");
#endif
	// we only continue if there are one and only one children with this tag name
	if (iNumChildrenByTagName == 1)
	{
		if (gDLL->getXMLIFace()->SetToChildByTagName(m_pFXml,szName))
		{
			// skip to the next non-comment node
			if (SkipToNextVal())
			{
				// get the string value of the current xml node
				bool success = SafeGetLastNodeValue(m_pFXml,pszVal,pszDefault);
				gDLL->getXMLIFace()->SetToParent(m_pFXml);
				return success;
			}
			// otherwise we can't find a non-comment node on this level so we will FAssert and return false
			else
			{
				FAssertMsg(false, "Error in GetChildXmlValByName function, unable to find the next non-comment node");
				gDLL->getXMLIFace()->SetToParent(m_pFXml);
				return false;
			}
		}
		// otherwise there are no child nodes but we were expecting them so FAssert and return false
		else
		{
//			FAssertMsg(false, "Error in GetChildXmlValByName function, unable to find a specified node");
			return false;
		}
	}
	else
	{
		//FAssertMsg(false, "Error in GetChildXmlValByName function, unable to find a specified node");
		return false;
	}
}

//
//------------------------------------------------------------------------------------------------------
bool CvXMLLoadUtility::GetChildXmlValByName(std::wstring& pszVal, const TCHAR* szName, wchar* pszDefault)
{
	int iNumChildrenByTagName=1;

	if (pszDefault)
	{
		pszVal=pszDefault;
	}
	else
	{
		pszVal.clear();
	}

#if 0
	iNumChildrenByTagName = gDLL->getXMLIFace()->NumOfChildrenByTagName(m_pFXml,szName);
	FAssertMsg((iNumChildrenByTagName < 2),"More children with tag name than expected, should only be 1.");
#endif
	// we only continue if there are one and only one children with this tag name
	if (iNumChildrenByTagName == 1)
	{
		if (gDLL->getXMLIFace()->SetToChildByTagName(m_pFXml,szName))
		{
			// skip to the next non-comment node
			if (SkipToNextVal())
			{
				// get the string value of the current xml node
				bool success = SafeGetLastNodeValue(m_pFXml,pszVal,pszDefault);
				gDLL->getXMLIFace()->SetToParent(m_pFXml);
				return success;
			}
			// otherwise we can't find a non-comment node on this level so we will FAssert and return false
			else
			{
				FAssertMsg(false, "Error in GetChildXmlValByName function, unable to find the next non-comment node");
				gDLL->getXMLIFace()->SetToParent(m_pFXml);
				return false;
			}
		}
		// otherwise there are no child nodes but we were expecting them so FAssert and return false
		else
		{
//			FAssertMsg(false, "Error in GetChildXmlValByName function, unable to find a specified node");
			return false;
		}
	}
	else
	{
		//FAssertMsg(false, "Error in GetChildXmlValByName function, unable to find a specified node");
		return false;
	}
}

//------------------------------------------------------------------------------------------------------
//
//  FUNCTION:   GetChildXmlValByName(int* piVal, const TCHAR* szName, int iDefault = 0)
//
//  PURPOSE :   Overloaded function that gets the child value of the tag with szName if there is only one child
// 				value of that name
//
//------------------------------------------------------------------------------------------------------
bool CvXMLLoadUtility::GetChildXmlValByName(int* piVal, const TCHAR* szName, int iDefault)
{
	int iNumChildrenByTagName=1;

	// set the value to the default
	*piVal = iDefault;

#if 0	// def _DEBUG
	iNumChildrenByTagName = gDLL->getXMLIFace()->NumOfChildrenByTagName(m_pFXml,szName);
	FAssertMsg((iNumChildrenByTagName < 2),"More children with tag name than expected, should only be 1.");
	// we only continue if there are one and only one children with this tag name
#endif
	if (iNumChildrenByTagName == 1)
	{
		if (gDLL->getXMLIFace()->SetToChildByTagName(m_pFXml,szName))
		{
			// skip to the next non-comment node
			if (SkipToNextVal())
			{
				// get the string value of the current xml node
				bool success = SafeGetLastNodeValue(m_pFXml,piVal,iDefault);
				gDLL->getXMLIFace()->SetToParent(m_pFXml);
				return success;
			}
			// otherwise we can't find a non-comment node on this level so we will FAssert and return false
			else
			{
				FAssertMsg(false, "Error in GetChildXmlValByName function, unable to find the next non-comment node");
				gDLL->getXMLIFace()->SetToParent(m_pFXml);
				return false;
			}
		}
		// otherwise there are no child nodes but we were expecting them so FAssert and return false
		else
		{
//			FAssertMsg(false, "Error in GetChildXmlValByName function, unable to find a specified node");
			return false;
		}
	}
	else
	{
		//FAssertMsg(false, "Error in GetChildXmlValByName function, unable to find a specified node");
		return false;
	}
}

//------------------------------------------------------------------------------------------------------
//
//  FUNCTION:   GetChildXmlValByName(float* pfVal, const TCHAR* szName, float fDefault = 0.0f)
//
//  PURPOSE :   Overloaded function that gets the child value of the tag with szName if there is only one child
// 				value of that name

//
//------------------------------------------------------------------------------------------------------
bool CvXMLLoadUtility::GetChildXmlValByName(float* pfVal, const TCHAR* szName, float fDefault)
{
	int iNumChildrenByTagName=1;

	// set the value to the default
	*pfVal = fDefault;
#if 0
	iNumChildrenByTagName = gDLL->getXMLIFace()->NumOfChildrenByTagName(m_pFXml,szName);
	FAssertMsg((iNumChildrenByTagName < 2),"More children with tag5 name than expected, should only be 1.");
#endif
	// we only continue if there are one and only one children with this tag name
	if (iNumChildrenByTagName == 1)
	{
		if (gDLL->getXMLIFace()->SetToChildByTagName(m_pFXml,szName))
		{
			// skip to the next non-comment node
			if (SkipToNextVal())
			{
				// get the string value of the current xml node
				bool success = SafeGetLastNodeValue(m_pFXml,pfVal,fDefault);
				gDLL->getXMLIFace()->SetToParent(m_pFXml);
				return success;
			}
			// otherwise we can't find a non-comment node on this level so we will FAssert and return false
			else
			{
				FAssertMsg(false, "Error in GetChildXmlValByName function, unable to find the next non-comment node");
				gDLL->getXMLIFace()->SetToParent(m_pFXml);
				return false;
			}
		}
		// otherwise there are no child nodes but we were expecting them so FAssert and return false
		else
		{
//			FAssertMsg(false, "Error in GetChildXmlValByName function, unable to find a specified node");
			return false;
		}
	}
	else
	{
		//FAssertMsg(false, "Error in GetChildXmlValByName function, unable to find a specified node");
		return false;
	}
}

//------------------------------------------------------------------------------------------------------
//
//  FUNCTION:   GetChildXmlValByName(bool* pbVal, const TCHAR* szName, bool bDefault = false)
//
//  PURPOSE :   Overloaded function that gets the child value of the tag with szName if there is only one child
// 				value of that name

//
//------------------------------------------------------------------------------------------------------
bool CvXMLLoadUtility::GetChildXmlValByName(bool* pbVal, const TCHAR* szName, bool bDefault)
{
	int iNumChildrenByTagName=1;

	// set the boolean value to it's default value
	*pbVal = bDefault;

#if 0
	iNumChildrenByTagName = gDLL->getXMLIFace()->NumOfChildrenByTagName(m_pFXml,szName);
	FAssertMsg((iNumChildrenByTagName < 2),"More children with tag name than expected, should only be 1.");
#endif
	// we only continue if there are one and only one children with this tag name
	if (iNumChildrenByTagName == 1)
	{
		if (gDLL->getXMLIFace()->SetToChildByTagName(m_pFXml,szName))
		{
			// skip to the next non-comment node
			if (SkipToNextVal())
			{
				// get the string value of the current xml node
				bool success = SafeGetLastNodeValue(m_pFXml,pbVal,bDefault);
				gDLL->getXMLIFace()->SetToParent(m_pFXml);
				return success;
			}
			// otherwise we can't find a non-comment node on this level so we will FAssert and return false
			else
			{
				FAssertMsg(false, "Error in GetChildXmlValByName function, unable to find the next non-comment node");
				gDLL->getXMLIFace()->SetToParent(m_pFXml);
				return false;
			}
		}
		// otherwise there are no child nodes but we were expecting them so FAssert and return false
		else
		{
//			FAssertMsg(false, "Error in GetChildXmlValByName function, unable to find a specified node");
			return false;
		}
	}
	else
	{
		//FAssertMsg(false, "Error in GetChildXmlValByName function, unable to find a specified node");
		return false;
	}
}

//------------------------------------------------------------------------------------------------------
//
//  FUNCTION:   GetHotKeyInt(TCHAR* pszHotKeyVal)
//
//  PURPOSE :   returns either the integer value of the keyboard mapping for the hot key or -1 if it
//				doesn't exist.
//
//------------------------------------------------------------------------------------------------------
int CvXMLLoadUtility::GetHotKeyInt(const TCHAR* pszHotKeyVal)
{
	// SPEEDUP
	PROFILE("GetHotKeyInt");
	/* rewrite by lol for performance

	int i;

	struct CvKeyBoardMapping
	{
		TCHAR szDefineString[25];
		int iIntVal;
	};


	const int iNumKeyBoardMappings=108;
	const CvKeyBoardMapping asCvKeyBoardMapping[iNumKeyBoardMappings] =
	{
		{"KB_ESCAPE",FInputDevice::KB_ESCAPE},
		{"KB_0",FInputDevice::KB_0},
		{"KB_1",FInputDevice::KB_1},
		{"KB_2",FInputDevice::KB_2},
		{"KB_3",FInputDevice::KB_3},
		{"KB_4",FInputDevice::KB_4},
		{"KB_5",FInputDevice::KB_5},
		{"KB_6",FInputDevice::KB_6},
		{"KB_7",FInputDevice::KB_7},
		{"KB_8",FInputDevice::KB_8},
		{"KB_9",FInputDevice::KB_9},
		{"KB_MINUS",FInputDevice::KB_MINUS},	    // - on main keyboard
		{"KB_A",FInputDevice::KB_A},
		{"KB_B",FInputDevice::KB_B},
		{"KB_C",FInputDevice::KB_C},
		{"KB_D",FInputDevice::KB_D},
		{"KB_E",FInputDevice::KB_E},
		{"KB_F",FInputDevice::KB_F},
		{"KB_G",FInputDevice::KB_G},
		{"KB_H",FInputDevice::KB_H},
		{"KB_I",FInputDevice::KB_I},
		{"KB_J",FInputDevice::KB_J},
		{"KB_K",FInputDevice::KB_K},
		{"KB_L",FInputDevice::KB_L},
		{"KB_M",FInputDevice::KB_M},
		{"KB_N",FInputDevice::KB_N},
		{"KB_O",FInputDevice::KB_O},
		{"KB_P",FInputDevice::KB_P},
		{"KB_Q",FInputDevice::KB_Q},
		{"KB_R",FInputDevice::KB_R},
		{"KB_S",FInputDevice::KB_S},
		{"KB_T",FInputDevice::KB_T},
		{"KB_U",FInputDevice::KB_U},
		{"KB_V",FInputDevice::KB_V},
		{"KB_W",FInputDevice::KB_W},
		{"KB_X",FInputDevice::KB_X},
		{"KB_Y",FInputDevice::KB_Y},
		{"KB_Z",FInputDevice::KB_Z},
		{"KB_EQUALS",FInputDevice::KB_EQUALS},
		{"KB_BACKSPACE",FInputDevice::KB_BACKSPACE},
		{"KB_TAB",FInputDevice::KB_TAB},
		{"KB_LBRACKET",FInputDevice::KB_LBRACKET},
		{"KB_RBRACKET",FInputDevice::KB_RBRACKET},
		{"KB_RETURN",FInputDevice::KB_RETURN},		// Enter on main keyboard
		{"KB_LCONTROL",FInputDevice::KB_LCONTROL},
		{"KB_SEMICOLON",FInputDevice::KB_SEMICOLON},
		{"KB_APOSTROPHE",FInputDevice::KB_APOSTROPHE},
		{"KB_GRAVE",FInputDevice::KB_GRAVE},		// accent grave
		{"KB_LSHIFT",FInputDevice::KB_LSHIFT},
		{"KB_BACKSLASH",FInputDevice::KB_BACKSLASH},
		{"KB_COMMA",FInputDevice::KB_COMMA},
		{"KB_PERIOD",FInputDevice::KB_PERIOD},
		{"KB_SLASH",FInputDevice::KB_SLASH},
		{"KB_RSHIFT",FInputDevice::KB_RSHIFT},
		{"KB_NUMPADSTAR",FInputDevice::KB_NUMPADSTAR},
		{"KB_LALT",FInputDevice::KB_LALT},
		{"KB_SPACE",FInputDevice::KB_SPACE},
		{"KB_CAPSLOCK",FInputDevice::KB_CAPSLOCK},
		{"KB_F1",FInputDevice::KB_F1},
		{"KB_F2",FInputDevice::KB_F2},
		{"KB_F3",FInputDevice::KB_F3},
		{"KB_F4",FInputDevice::KB_F4},
		{"KB_F5",FInputDevice::KB_F5},
		{"KB_F6",FInputDevice::KB_F6},
		{"KB_F7",FInputDevice::KB_F7},
		{"KB_F8",FInputDevice::KB_F8},
		{"KB_F9",FInputDevice::KB_F9},
		{"KB_F10",FInputDevice::KB_F10},
		{"KB_NUMLOCK",FInputDevice::KB_NUMLOCK},
		{"KB_SCROLL",FInputDevice::KB_SCROLL},
		{"KB_NUMPAD7",FInputDevice::KB_NUMPAD7},
		{"KB_NUMPAD8",FInputDevice::KB_NUMPAD8},
		{"KB_NUMPAD9",FInputDevice::KB_NUMPAD9},
		{"KB_NUMPADMINUS",FInputDevice::KB_NUMPADMINUS},
		{"KB_NUMPAD4",FInputDevice::KB_NUMPAD4},
		{"KB_NUMPAD5",FInputDevice::KB_NUMPAD5},
		{"KB_NUMPAD6",FInputDevice::KB_NUMPAD6},
		{"KB_NUMPADPLUS",FInputDevice::KB_NUMPADPLUS},
		{"KB_NUMPAD1",FInputDevice::KB_NUMPAD1},
		{"KB_NUMPAD2",FInputDevice::KB_NUMPAD2},
		{"KB_NUMPAD3",FInputDevice::KB_NUMPAD3},
		{"KB_NUMPAD0",FInputDevice::KB_NUMPAD0},
		{"KB_NUMPADPERIOD",FInputDevice::KB_NUMPADPERIOD}, 
		{"KB_F11",FInputDevice::KB_F11},
		{"KB_F12",FInputDevice::KB_F12},
		{"KB_NUMPADEQUALS",FInputDevice::KB_NUMPADEQUALS},
		{"KB_AT",FInputDevice::KB_AT},
		{"KB_UNDERLINE",FInputDevice::KB_UNDERLINE},
		{"KB_COLON",FInputDevice::KB_COLON},
		{"KB_NUMPADENTER",FInputDevice::KB_NUMPADENTER},
		{"KB_RCONTROL",FInputDevice::KB_RCONTROL},
		{"KB_VOLUMEDOWN",FInputDevice::KB_VOLUMEDOWN},
		{"KB_VOLUMEUP",FInputDevice::KB_VOLUMEUP},
		{"KB_NUMPADCOMMA",FInputDevice::KB_NUMPADCOMMA},
		{"KB_NUMPADSLASH",FInputDevice::KB_NUMPADSLASH},
		{"KB_SYSRQ",FInputDevice::KB_SYSRQ},
		{"KB_RALT",FInputDevice::KB_RALT},
		{"KB_PAUSE",FInputDevice::KB_PAUSE},
		{"KB_HOME",FInputDevice::KB_HOME},
		{"KB_UP",FInputDevice::KB_UP},
		{"KB_PGUP",FInputDevice::KB_PGUP},
		{"KB_LEFT",FInputDevice::KB_LEFT},
		{"KB_RIGHT",FInputDevice::KB_RIGHT},
		{"KB_END",FInputDevice::KB_END},
		{"KB_DOWN",FInputDevice::KB_DOWN},
		{"KB_PGDN",FInputDevice::KB_PGDN},
		{"KB_INSERT",FInputDevice::KB_INSERT},
		{"KB_DELETE",FInputDevice::KB_DELETE},
	};

	for (i=0;i<iNumKeyBoardMappings;i++)
	{
		if (strcmp(asCvKeyBoardMapping [i].szDefineString, pszHotKeyVal) == 0)
		{
			return asCvKeyBoardMapping[i].iIntVal;
		}
	}

	return -1;
	*/
	return gCvKeyBoardMapping.getKeyInt(pszHotKeyVal);
}


//
// lol for performance
// 

CvKeyBoardMapping gCvKeyBoardMapping;	// global single instance

CvKeyBoardMapping::Data *
CvKeyBoardMapping::bin_search(Data *v[], int begin, int end, const char *value) {
	int position;
	int cond = 0;
	while(begin <= end) {
		position = (begin + end) / 2;
		if((cond = ::strcmp(v[position]->pszKey, value)) == 0)
			return v[position];
		else if(cond < 0)
			begin = position + 1;
		else
			end = position - 1;
	}
	return NULL;
}

void CvKeyBoardMapping::endInsert()
{
	sort( _vec.begin(), _vec.end(), this->lesser );
	_b_filled = true;
}

void CvKeyBoardMapping::generateTable( )
{
	// 108
	if(_vec.size() != 0) return;

	_vec.reserve(108);

	insert("KB_ESCAPE", FInputDevice::KB_ESCAPE, gDLL->getText("TXT_KEY_KEYBOARD_ESCAPE"));
	insert("KB_0", FInputDevice::KB_0, L"0");
	insert("KB_1", FInputDevice::KB_1, L"1");
	insert("KB_2", FInputDevice::KB_2, L"2");
	insert("KB_3", FInputDevice::KB_3, L"3");
	insert("KB_4", FInputDevice::KB_4, L"4");
	insert("KB_5", FInputDevice::KB_5, L"5");
	insert("KB_6", FInputDevice::KB_6, L"6");
	insert("KB_7", FInputDevice::KB_7, L"7");
	insert("KB_8", FInputDevice::KB_8, L"8");
	insert("KB_9", FInputDevice::KB_9, L"9");
	insert("KB_MINUS", FInputDevice::KB_MINUS, L"-");	    /* - on main keyboard */
	insert("KB_A", FInputDevice::KB_A, L"A");
	insert("KB_B", FInputDevice::KB_B, L"B");
	insert("KB_C", FInputDevice::KB_C, L"C");
	insert("KB_D", FInputDevice::KB_D, L"D");
	insert("KB_E", FInputDevice::KB_E, L"E");
	insert("KB_F", FInputDevice::KB_F, L"F");
	insert("KB_G", FInputDevice::KB_G, L"G");
	insert("KB_H", FInputDevice::KB_H, L"H");
	insert("KB_I", FInputDevice::KB_I, L"I");
	insert("KB_J", FInputDevice::KB_J, L"J");
	insert("KB_K", FInputDevice::KB_K, L"K");
	insert("KB_L", FInputDevice::KB_L, L"L");
	insert("KB_M", FInputDevice::KB_M, L"M");
	insert("KB_N", FInputDevice::KB_N, L"N");
	insert("KB_O", FInputDevice::KB_O, L"O");
	insert("KB_P", FInputDevice::KB_P, L"P");
	insert("KB_Q", FInputDevice::KB_Q, L"Q");
	insert("KB_R", FInputDevice::KB_R, L"R");
	insert("KB_S", FInputDevice::KB_S, L"S");
	insert("KB_T", FInputDevice::KB_T, L"T");
	insert("KB_U", FInputDevice::KB_U, L"U");
	insert("KB_V", FInputDevice::KB_V, L"V");
	insert("KB_W", FInputDevice::KB_W, L"W");
	insert("KB_X", FInputDevice::KB_X, L"X");
	insert("KB_Y", FInputDevice::KB_Y, L"Y");
	insert("KB_Z", FInputDevice::KB_Z, L"Z");
	insert("KB_EQUALS", FInputDevice::KB_EQUALS, L"=");
	insert("KB_BACKSPACE", FInputDevice::KB_BACKSPACE, gDLL->getText("TXT_KEY_KEYBOARD_BACKSPACE"));
	insert("KB_TAB", FInputDevice::KB_TAB, L"TAB");
	insert("KB_LBRACKET", FInputDevice::KB_LBRACKET, L"[");
	insert("KB_RBRACKET", FInputDevice::KB_RBRACKET, L"]");
	insert("KB_RETURN", FInputDevice::KB_RETURN, gDLL->getText("TXT_KEY_KEYBOARD_ENTER"));		/* Enter on main keyboard */
	insert("KB_LCONTROL", FInputDevice::KB_LCONTROL, gDLL->getText("TXT_KEY_KEYBOARD_LEFT_CONTROL_KEY"));
	insert("KB_SEMICOLON", FInputDevice::KB_SEMICOLON, L";");
	insert("KB_APOSTROPHE", FInputDevice::KB_APOSTROPHE, L"'");
	insert("KB_GRAVE", FInputDevice::KB_GRAVE, L"`");		/* accent grave */
	insert("KB_LSHIFT", FInputDevice::KB_LSHIFT, gDLL->getText("TXT_KEY_KEYBOARD_LEFT_SHIFT_KEY"));
	insert("KB_BACKSLASH", FInputDevice::KB_BACKSLASH, L"\\");
	insert("KB_COMMA", FInputDevice::KB_COMMA, L",");
	insert("KB_PERIOD", FInputDevice::KB_PERIOD, L".");
	insert("KB_SLASH", FInputDevice::KB_SLASH, L"/");
	insert("KB_RSHIFT", FInputDevice::KB_RSHIFT, gDLL->getText("TXT_KEY_KEYBOARD_RIGHT_SHIFT_KEY"));
	insert("KB_NUMPADSTAR", FInputDevice::KB_NUMPADSTAR, gDLL->getText("TXT_KEY_KEYBOARD_NUM_PAD_STAR"));
	insert("KB_LALT", FInputDevice::KB_LALT, gDLL->getText("TXT_KEY_KEYBOARD_LEFT_ALT_KEY"));
	insert("KB_SPACE", FInputDevice::KB_SPACE, gDLL->getText("TXT_KEY_KEYBOARD_SPACE_KEY"));
	insert("KB_CAPSLOCK", FInputDevice::KB_CAPSLOCK, gDLL->getText("TXT_KEY_KEYBOARD_CAPS_LOCK"));
	insert("KB_F1", FInputDevice::KB_F1, L"F1");
	insert("KB_F2", FInputDevice::KB_F2, L"F2");
	insert("KB_F3", FInputDevice::KB_F3, L"F3");
	insert("KB_F4", FInputDevice::KB_F4, L"F4");
	insert("KB_F5", FInputDevice::KB_F5, L"F5");
	insert("KB_F6", FInputDevice::KB_F6, L"F6");
	insert("KB_F7", FInputDevice::KB_F7, L"F7");
	insert("KB_F8", FInputDevice::KB_F8, L"F8");
	insert("KB_F9", FInputDevice::KB_F9, L"F9");
	insert("KB_F10", FInputDevice::KB_F10, L"F10");
	insert("KB_NUMLOCK", FInputDevice::KB_NUMLOCK, gDLL->getText("TXT_KEY_KEYBOARD_NUM_LOCK"));
	insert("KB_SCROLL", FInputDevice::KB_SCROLL, gDLL->getText("TXT_KEY_KEYBOARD_SCROLL_KEY"));
	insert("KB_NUMPAD7", FInputDevice::KB_NUMPAD7, gDLL->getText("TXT_KEY_KEYBOARD_NUMPAD_NUMBER", 7));
	insert("KB_NUMPAD8", FInputDevice::KB_NUMPAD8, gDLL->getText("TXT_KEY_KEYBOARD_NUMPAD_NUMBER", 8));
	insert("KB_NUMPAD9", FInputDevice::KB_NUMPAD9, gDLL->getText("TXT_KEY_KEYBOARD_NUMPAD_NUMBER", 9));
	insert("KB_NUMPADMINUS", FInputDevice::KB_NUMPADMINUS, gDLL->getText("TXT_KEY_KEYBOARD_NUMPAD_MINUS"));
	insert("KB_NUMPAD4", FInputDevice::KB_NUMPAD4, gDLL->getText("TXT_KEY_KEYBOARD_NUMPAD_NUMBER", 4));
	insert("KB_NUMPAD5", FInputDevice::KB_NUMPAD5, gDLL->getText("TXT_KEY_KEYBOARD_NUMPAD_NUMBER", 5));
	insert("KB_NUMPAD6", FInputDevice::KB_NUMPAD6, gDLL->getText("TXT_KEY_KEYBOARD_NUMPAD_NUMBER", 6));
	insert("KB_NUMPADPLUS", FInputDevice::KB_NUMPADPLUS, gDLL->getText("TXT_KEY_KEYBOARD_NUMPAD_PLUS"));
	insert("KB_NUMPAD1", FInputDevice::KB_NUMPAD1, gDLL->getText("TXT_KEY_KEYBOARD_NUMPAD_NUMBER", 1));
	insert("KB_NUMPAD2", FInputDevice::KB_NUMPAD2, gDLL->getText("TXT_KEY_KEYBOARD_NUMPAD_NUMBER", 2));
	insert("KB_NUMPAD3", FInputDevice::KB_NUMPAD3, gDLL->getText("TXT_KEY_KEYBOARD_NUMPAD_NUMBER", 3));
	insert("KB_NUMPAD0", FInputDevice::KB_NUMPAD0, gDLL->getText("TXT_KEY_KEYBOARD_NUMPAD_NUMBER", 0));
	insert("KB_NUMPADPERIOD", FInputDevice::KB_NUMPADPERIOD, gDLL->getText("TXT_KEY_KEYBOARD_NUMPAD_PERIOD"));
	insert("KB_F11", FInputDevice::KB_F11, L"F11");
	insert("KB_F12", FInputDevice::KB_F12, L"F12");
	insert("KB_NUMPADEQUALS", FInputDevice::KB_NUMPADEQUALS, gDLL->getText("TXT_KEY_KEYBOARD_NUMPAD_EQUALS"));
	insert("KB_AT", FInputDevice::KB_AT, L"@");
	insert("KB_UNDERLINE", FInputDevice::KB_UNDERLINE, L"_");
	insert("KB_COLON", FInputDevice::KB_COLON, L":");
	insert("KB_NUMPADENTER", FInputDevice::KB_NUMPADENTER, gDLL->getText("TXT_KEY_KEYBOARD_NUMPAD_ENTER_KEY"));
	insert("KB_RCONTROL", FInputDevice::KB_RCONTROL, gDLL->getText("TXT_KEY_KEYBOARD_RIGHT_CONTROL_KEY"));
	insert("KB_VOLUMEDOWN", FInputDevice::KB_VOLUMEDOWN, gDLL->getText("TXT_KEY_KEYBOARD_VOLUME_DOWN"));
	insert("KB_VOLUMEUP", FInputDevice::KB_VOLUMEUP, gDLL->getText("TXT_KEY_KEYBOARD_VOLUME_UP"));
	insert("KB_NUMPADCOMMA", FInputDevice::KB_NUMPADCOMMA, gDLL->getText("TXT_KEY_KEYBOARD_NUMPAD_COMMA"));
	insert("KB_NUMPADSLASH", FInputDevice::KB_NUMPADSLASH, gDLL->getText("TXT_KEY_KEYBOARD_NUMPAD_SLASH"));
	insert("KB_SYSRQ", FInputDevice::KB_SYSRQ, gDLL->getText("TXT_KEY_KEYBOARD_SYSRQ"));
	insert("KB_RALT", FInputDevice::KB_RALT, gDLL->getText("TXT_KEY_KEYBOARD_RIGHT_ALT_KEY"));
	insert("KB_PAUSE", FInputDevice::KB_PAUSE, gDLL->getText("TXT_KEY_KEYBOARD_PAUSE_KEY"));
	insert("KB_HOME", FInputDevice::KB_HOME, gDLL->getText("TXT_KEY_KEYBOARD_HOME_KEY"));
	insert("KB_UP", FInputDevice::KB_UP, gDLL->getText("TXT_KEY_KEYBOARD_UP_ARROW"));
	insert("KB_PGUP", FInputDevice::KB_PGUP, gDLL->getText("TXT_KEY_KEYBOARD_PAGE_UP"));
	insert("KB_LEFT", FInputDevice::KB_LEFT, gDLL->getText("TXT_KEY_KEYBOARD_LEFT_ARROW"));
	insert("KB_RIGHT", FInputDevice::KB_RIGHT, gDLL->getText("TXT_KEY_KEYBOARD_RIGHT_ARROW"));
	insert("KB_END", FInputDevice::KB_END, gDLL->getText("TXT_KEY_KEYBOARD_END_KEY"));
	insert("KB_DOWN", FInputDevice::KB_DOWN, gDLL->getText("TXT_KEY_KEYBOARD_DOWN_ARROW"));
	insert("KB_PGDN", FInputDevice::KB_PGDN, gDLL->getText("TXT_KEY_KEYBOARD_PAGE_DOWN"));
	insert("KB_INSERT", FInputDevice::KB_INSERT, gDLL->getText("TXT_KEY_KEYBOARD_INSERT_KEY"));
	insert("KB_DELETE", FInputDevice::KB_DELETE, gDLL->getText("TXT_KEY_KEYBOARD_DELETE_KEY"));
	
	endInsert();
}
