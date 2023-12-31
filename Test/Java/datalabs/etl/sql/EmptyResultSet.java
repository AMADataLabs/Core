package datalabs.etl.sql;

import java.util.Calendar;
import java.io.Reader;
import java.io.InputStream;
import java.math.BigDecimal;
import java.sql.Array;
import java.sql.Blob;
import java.sql.Clob;
import java.sql.NClob;
import java.sql.Ref;
import java.sql.ResultSet;
import java.sql.ResultSetMetaData;
import java.sql.RowId;
import java.sql.SQLException;
import java.sql.SQLWarning;
import java.sql.SQLXML;
import java.sql.Statement;
import java.sql.Wrapper;


class EmptyResultSetMetaData implements ResultSetMetaData {
    public int getColumnCount() throws SQLException { return 0; }
    public boolean isAutoIncrement(int column) throws SQLException { return false; }
    public boolean isCaseSensitive(int column) throws SQLException { return false; }
    public boolean isSearchable(int column) throws SQLException { return false; }
    public boolean isCurrency(int column) throws SQLException { return false; }
    public int isNullable(int column) throws SQLException { return 0; }
    public boolean isSigned(int column) throws SQLException { return false; }
    public int getColumnDisplaySize(int column) throws SQLException { return 0; }
    public String getColumnLabel(int column) throws SQLException { return null; }
    public String getColumnName(int column) throws SQLException { return null; }
    public String getSchemaName(int column) throws SQLException { return null; }
    public int getPrecision(int column) throws SQLException { return 0; }
    public int getScale(int column) throws SQLException { return 0; }
    public String getTableName(int column) throws SQLException { return null; }
    public String getCatalogName(int column) throws SQLException { return null; }
    public int getColumnType(int column) throws SQLException { return 0; }
    public String getColumnTypeName(int column) throws SQLException { return null; }
    public boolean isReadOnly(int column) throws SQLException { return false; }
    public boolean isWritable(int column) throws SQLException { return false; }
    public boolean isDefinitelyWritable(int column) throws SQLException { return false; }
    public String getColumnClassName(int column) throws SQLException { return null; }

    public <T> T unwrap(Class<T> iface) throws SQLException { return null; }
    public boolean isWrapperFor(Class<?> iface) throws SQLException { return false; }
}


public class EmptyResultSet implements ResultSet {

    public boolean next() throws SQLException {
        return false;
    }

    public ResultSetMetaData getMetaData() throws SQLException {
        return new EmptyResultSetMetaData();
    }

    public void close() throws SQLException { }
    public boolean wasNull() throws SQLException { return false; }
    public String getString(int columnIndex) throws SQLException { return null; }
    public boolean getBoolean(int columnIndex) throws SQLException { return false; }
    public byte getByte(int columnIndex) throws SQLException { return (byte) 0; }
    public short getShort(int columnIndex) throws SQLException { return (short) 0; }
    public int getInt(int columnIndex) throws SQLException { return 0; }
    public long getLong(int columnIndex) throws SQLException { return (long) 0; }
    public float getFloat(int columnIndex) throws SQLException { return (float) 0.0; }
    public double getDouble(int columnIndex) throws SQLException { return 0.0; }
    public BigDecimal getBigDecimal(int columnIndex, int scale) throws SQLException { return null; }
    public byte[] getBytes(int columnIndex) throws SQLException { return new byte[0]; }
    public java.sql.Date getDate(int columnIndex) throws SQLException { return null; }
    public java.sql.Time getTime(int columnIndex) throws SQLException { return null; }
    public java.sql.Timestamp getTimestamp(int columnIndex) throws SQLException { return null; }
    public java.io.InputStream getAsciiStream(int columnIndex) throws SQLException { return null; }
    public java.io.InputStream getUnicodeStream(int columnIndex) throws SQLException { return null; }
    public java.io.InputStream getBinaryStream(int columnIndex) throws SQLException { return null; }
    public String getString(String columnLabel) throws SQLException { return null; }
    public boolean getBoolean(String columnLabel) throws SQLException { return false; }
    public byte getByte(String columnLabel) throws SQLException { return (byte) 0; }
    public short getShort(String columnLabel) throws SQLException { return (short) 0; }
    public int getInt(String columnLabel) throws SQLException { return 0; }
    public long getLong(String columnLabel) throws SQLException { return 0; }
    public float getFloat(String columnLabel) throws SQLException { return (float) 0.0; }
    public double getDouble(String columnLabel) throws SQLException { return 0.0; }
    public BigDecimal getBigDecimal(String columnLabel, int scale) throws SQLException { return null; }
    public byte[] getBytes(String columnLabel) throws SQLException { return new byte[0]; }
    public java.sql.Date getDate(String columnLabel) throws SQLException { return null; }
    public java.sql.Time getTime(String columnLabel) throws SQLException { return null; }
    public java.sql.Timestamp getTimestamp(String columnLabel) throws SQLException { return null; }
    public java.io.InputStream getAsciiStream(String columnLabel) throws SQLException { return null; }
    public java.io.InputStream getUnicodeStream(String columnLabel) throws SQLException { return null; }
    public java.io.InputStream getBinaryStream(String columnLabel) throws SQLException { return null; }
    public SQLWarning getWarnings() throws SQLException { return null; }
    public void clearWarnings() throws SQLException { }
    public String getCursorName() throws SQLException { return null; }
    public Object getObject(int columnIndex) throws SQLException { return null; }
    public Object getObject(String columnLabel) throws SQLException { return null; }
    public int findColumn(String columnLabel) throws SQLException { return 0; }
    public java.io.Reader getCharacterStream(int columnIndex) throws SQLException { return null; }
    public java.io.Reader getCharacterStream(String columnLabel) throws SQLException { return null; }
    public BigDecimal getBigDecimal(int columnIndex) throws SQLException { return null; }
    public BigDecimal getBigDecimal(String columnLabel) throws SQLException { return null; }
    public boolean isBeforeFirst() throws SQLException { return false; }
    public boolean isAfterLast() throws SQLException { return false; }
    public boolean isFirst() throws SQLException { return false; }
    public boolean isLast() throws SQLException { return false; }
    public void beforeFirst() throws SQLException { }
    public void afterLast() throws SQLException { }
    public boolean first() throws SQLException { return false; }
    public boolean last() throws SQLException { return false; }
    public int getRow() throws SQLException { return 0; }
    public boolean absolute( int row ) throws SQLException { return false; }
    public boolean relative( int rows ) throws SQLException { return false; }
    public boolean previous() throws SQLException { return false; }
    public void setFetchDirection(int direction) throws SQLException { }
    public int getFetchDirection() throws SQLException { return 0; }
    public void setFetchSize(int rows) throws SQLException { }
    public int getFetchSize() throws SQLException { return 0; }
    public int getType() throws SQLException { return 0; }
    public int getConcurrency() throws SQLException { return 0; }
    public boolean rowUpdated() throws SQLException { return false; }
    public boolean rowInserted() throws SQLException { return false; }
    public boolean rowDeleted() throws SQLException { return false; }
    public void updateNull(int columnIndex) throws SQLException {}
    public void updateBoolean(int columnIndex, boolean x) throws SQLException { }
    public void updateByte(int columnIndex, byte x) throws SQLException { }
    public void updateShort(int columnIndex, short x) throws SQLException { }
    public void updateInt(int columnIndex, int x) throws SQLException { }
    public void updateLong(int columnIndex, long x) throws SQLException { }
    public void updateFloat(int columnIndex, float x) throws SQLException { }
    public void updateDouble(int columnIndex, double x) throws SQLException { }
    public void updateBigDecimal(int columnIndex, BigDecimal x) throws SQLException { }
    public void updateString(int columnIndex, String x) throws SQLException { }
    public void updateBytes(int columnIndex, byte x[]) throws SQLException { }
    public void updateDate(int columnIndex, java.sql.Date x) throws SQLException { }
    public void updateTime(int columnIndex, java.sql.Time x) throws SQLException { }
    public void updateTimestamp(int columnIndex, java.sql.Timestamp x) throws SQLException { }
    public void updateAsciiStream(int columnIndex, java.io.InputStream x, int length) throws SQLException { }
    public void updateBinaryStream(int columnIndex, java.io.InputStream x, int length) throws SQLException { }
    public void updateCharacterStream(int columnIndex, java.io.Reader x, int length) throws SQLException { }
    public void updateObject(int columnIndex, Object x, int scaleOrLength) throws SQLException { }
    public void updateObject(int columnIndex, Object x) throws SQLException { }
    public void updateNull(String columnLabel) throws SQLException { }
    public void updateBoolean(String columnLabel, boolean x) throws SQLException { }
    public void updateByte(String columnLabel, byte x) throws SQLException { }
    public void updateShort(String columnLabel, short x) throws SQLException { }
    public void updateInt(String columnLabel, int x) throws SQLException { }
    public void updateLong(String columnLabel, long x) throws SQLException { }
    public void updateFloat(String columnLabel, float x) throws SQLException { }
    public void updateDouble(String columnLabel, double x) throws SQLException { }
    public void updateBigDecimal(String columnLabel, BigDecimal x) throws SQLException { }
    public void updateString(String columnLabel, String x) throws SQLException { }
    public void updateBytes(String columnLabel, byte x[]) throws SQLException { }
    public void updateDate(String columnLabel, java.sql.Date x) throws SQLException { }
    public void updateTime(String columnLabel, java.sql.Time x) throws SQLException { }
    public void updateTimestamp(String columnLabel, java.sql.Timestamp x) throws SQLException { }
    public void updateAsciiStream(String columnLabel, java.io.InputStream x, int length) throws SQLException { }
    public void updateBinaryStream(String columnLabel, java.io.InputStream x, int length) throws SQLException { }
    public void updateCharacterStream(String columnLabel, java.io.Reader reader, int length) throws SQLException { }
    public void updateObject(String columnLabel, Object x, int scaleOrLength) throws SQLException { }
    public void updateObject(String columnLabel, Object x) throws SQLException { }
    public void insertRow() throws SQLException { }
    public void updateRow() throws SQLException { }
    public void deleteRow() throws SQLException { }
    public void refreshRow() throws SQLException { }
    public void cancelRowUpdates() throws SQLException { }
    public void moveToInsertRow() throws SQLException { }
    public void moveToCurrentRow() throws SQLException { }
    public Statement getStatement() throws SQLException { return null; }
    public Object getObject(int columnIndex, java.util.Map<String,Class<?>> map) throws SQLException { return null; }
    public Ref getRef(int columnIndex) throws SQLException { return null; }
    public Blob getBlob(int columnIndex) throws SQLException { return null; }
    public Clob getClob(int columnIndex) throws SQLException { return null; }
    public Array getArray(int columnIndex) throws SQLException { return null; }
    public Object getObject(String columnLabel, java.util.Map<String,Class<?>> map) throws SQLException { return null; }
    public Ref getRef(String columnLabel) throws SQLException { return null; }
    public Blob getBlob(String columnLabel) throws SQLException { return null; }
    public Clob getClob(String columnLabel) throws SQLException { return null; }
    public Array getArray(String columnLabel) throws SQLException { return null; }
    public java.sql.Date getDate(int columnIndex, Calendar cal) throws SQLException { return null; }
    public java.sql.Date getDate(String columnLabel, Calendar cal) throws SQLException { return null; }
    public java.sql.Time getTime(int columnIndex, Calendar cal) throws SQLException { return null; }
    public java.sql.Time getTime(String columnLabel, Calendar cal) throws SQLException { return null; }
    public java.sql.Timestamp getTimestamp(int columnIndex, Calendar cal) throws SQLException { return null; }
    public java.sql.Timestamp getTimestamp(String columnLabel, Calendar cal) throws SQLException { return null; }
    public java.net.URL getURL(int columnIndex) throws SQLException { return null; }
    public java.net.URL getURL(String columnLabel) throws SQLException { return null; }
    public void updateRef(int columnIndex, java.sql.Ref x) throws SQLException { }
    public void updateRef(String columnLabel, java.sql.Ref x) throws SQLException { }
    public void updateBlob(int columnIndex, java.sql.Blob x) throws SQLException { }
    public void updateBlob(String columnLabel, java.sql.Blob x) throws SQLException { }
    public void updateClob(int columnIndex, java.sql.Clob x) throws SQLException { }
    public void updateClob(String columnLabel, java.sql.Clob x) throws SQLException { }
    public void updateArray(int columnIndex, java.sql.Array x) throws SQLException { }
    public void updateArray(String columnLabel, java.sql.Array x) throws SQLException { }
    public RowId getRowId(int columnIndex) throws SQLException { return null; }
    public RowId getRowId(String columnLabel) throws SQLException { return null; }
    public void updateRowId(int columnIndex, RowId x) throws SQLException { }
    public void updateRowId(String columnLabel, RowId x) throws SQLException { }
    public int getHoldability() throws SQLException { return 0; }
    public boolean isClosed() throws SQLException { return false; }
    public void updateNString(int columnIndex, String nString) throws SQLException { }
    public void updateNString(String columnLabel, String nString) throws SQLException { }
    public void updateNClob(int columnIndex, NClob nClob) throws SQLException { }
    public void updateNClob(String columnLabel, NClob nClob) throws SQLException { }
    public NClob getNClob(int columnIndex) throws SQLException { return null; }
    public NClob getNClob(String columnLabel) throws SQLException { return null; }
    public SQLXML getSQLXML(int columnIndex) throws SQLException { return null; }
    public SQLXML getSQLXML(String columnLabel) throws SQLException { return null; }
    public void updateSQLXML(int columnIndex, SQLXML xmlObject) throws SQLException { }
    public void updateSQLXML(String columnLabel, SQLXML xmlObject) throws SQLException { }
    public String getNString(int columnIndex) throws SQLException { return null; }
    public String getNString(String columnLabel) throws SQLException { return null; }
    public java.io.Reader getNCharacterStream(int columnIndex) throws SQLException { return null; }
    public java.io.Reader getNCharacterStream(String columnLabel) throws SQLException { return null; }
    public void updateNCharacterStream(int columnIndex, java.io.Reader x, long length) throws SQLException { }
    public void updateNCharacterStream(String columnLabel, java.io.Reader reader, long length) throws SQLException { }
    public void updateAsciiStream(int columnIndex, java.io.InputStream x, long length) throws SQLException { }
    public void updateBinaryStream(int columnIndex, java.io.InputStream x, long length) throws SQLException { }
    public void updateCharacterStream(int columnIndex, java.io.Reader x, long length) throws SQLException { }
    public void updateAsciiStream(String columnLabel, java.io.InputStream x, long length) throws SQLException { }
    public void updateBinaryStream(String columnLabel, java.io.InputStream x, long length) throws SQLException { }
    public void updateCharacterStream(String columnLabel, java.io.Reader reader, long length) throws SQLException { }
    public void updateBlob(int columnIndex, InputStream inputStream, long length) throws SQLException { }
    public void updateBlob(String columnLabel, InputStream inputStream, long length) throws SQLException { }
    public void updateClob(int columnIndex,  Reader reader, long length) throws SQLException { }
    public void updateClob(String columnLabel,  Reader reader, long length) throws SQLException { }
    public void updateNClob(int columnIndex,  Reader reader, long length) throws SQLException { }
    public void updateNClob(String columnLabel,  Reader reader, long length) throws SQLException { }
    public void updateNCharacterStream(int columnIndex, java.io.Reader x) throws SQLException { }
    public void updateNCharacterStream(String columnLabel, java.io.Reader reader) throws SQLException { }
    public void updateAsciiStream(int columnIndex, java.io.InputStream x) throws SQLException { }
    public void updateBinaryStream(int columnIndex, java.io.InputStream x) throws SQLException { }
    public void updateCharacterStream(int columnIndex, java.io.Reader x) throws SQLException { }
    public void updateAsciiStream(String columnLabel, java.io.InputStream x) throws SQLException { }
    public void updateBinaryStream(String columnLabel, java.io.InputStream x) throws SQLException { }
    public void updateCharacterStream(String columnLabel, java.io.Reader reader) throws SQLException { }
    public void updateBlob(int columnIndex, InputStream inputStream) throws SQLException { }
    public void updateBlob(String columnLabel, InputStream inputStream) throws SQLException { }
    public void updateClob(int columnIndex,  Reader reader) throws SQLException { }
    public void updateClob(String columnLabel,  Reader reader) throws SQLException { }
    public void updateNClob(int columnIndex,  Reader reader) throws SQLException { }
    public void updateNClob(String columnLabel,  Reader reader) throws SQLException { }
    public <T> T getObject(int columnIndex, Class<T> type) throws SQLException { return null; }
    public <T> T getObject(String columnLabel, Class<T> type) throws SQLException { return null; }

    public <T> T unwrap(Class<T> iface) throws SQLException { return null; }
    public boolean isWrapperFor(Class<?> iface) throws SQLException { return false; }
}
