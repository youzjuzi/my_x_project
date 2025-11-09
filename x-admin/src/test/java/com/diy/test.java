package com.diy;

import lombok.extern.slf4j.Slf4j;
import org.junit.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.jdbc.core.JdbcTemplate;

import javax.annotation.Resource;
import javax.sql.DataSource;
import java.sql.SQLException;

@Slf4j
@SpringBootTest
public class test {

    @Resource
    DataSource dataSource;

    @Test
    public void getConnetion() throws SQLException {
        System.out.println(dataSource.getConnection());
    }
}