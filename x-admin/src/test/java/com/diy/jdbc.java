package com.diy;

import java.sql.*;

public class jdbc {
    public static void main(String[] args) {
        try {
            // 获取数据库连接
            Connection conn = DriverManager.getConnection("jdbc:mysql://localhost:3306/jdbc", "root", "123456");

            // 查询1: 根据用户输入工资，给出所有工资比这个工资高的教师姓名，年龄，性别及工资
            double inputSalary = 6000.0; // 用户输入的工资
            String query1 = "SELECT Tname, Tage, Tsex, Salary FROM Teacher JOIN Work ON Teacher.Tno = Work.Tno WHERE Salary > ?";
            PreparedStatement stmt1 = conn.prepareStatement(query1);
            stmt1.setDouble(1, inputSalary);
            ResultSet rs1 = stmt1.executeQuery();
            while (rs1.next()) {
                String name = rs1.getString("Tname");
                int age = rs1.getInt("Tage");
                String sex = rs1.getString("Tsex");
                double salary = rs1.getDouble("Salary");
                System.out.println("Name: " + name + ", Age: " + age + ", Sex: " + sex + ", Salary: " + salary);
            }
            System.out.println("Query 1 finished.");
            // 2. 根据用户输入的工资，将所有比这个工资低的教师工资都改为与之相同。
            double inputSalary2 = 500000.0; // 用户输入的工资
            String query2 = "UPDATE Work SET Salary = ? WHERE Salary < ?";
            PreparedStatement stmt2 = conn.prepareStatement(query2);
            stmt2.setDouble(1, inputSalary2);
            stmt2.setDouble(2, inputSalary2);
            int rs2 = stmt2.executeUpdate();
            System.out.println("Query 2 finished.");
        } catch (SQLException e) {
            throw new RuntimeException(e);
        }
    }
}