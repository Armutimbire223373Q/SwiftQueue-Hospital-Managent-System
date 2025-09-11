import React, { useState } from "react";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardDescription,
} from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Button } from "@/components/ui/button";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Badge } from "@/components/ui/badge";
import { Calendar } from "@/components/ui/calendar";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { DragDropContext, Droppable, Draggable } from "react-beautiful-dnd";
import {
  AlertCircle,
  Calendar as CalendarIcon,
  Clock,
  Users,
} from "lucide-react";

interface Staff {
  id: string;
  name: string;
  role: string;
  avatar: string;
  status: "available" | "busy" | "break" | "offline";
  counter?: number;
  efficiency?: number;
}

interface Counter {
  id: number;
  name: string;
  serviceType: string;
  assignedStaff?: Staff;
  status: "open" | "closed" | "maintenance";
}

interface Shift {
  id: string;
  staffId: string;
  staffName: string;
  date: Date;
  startTime: string;
  endTime: string;
  counter: number;
}

const StaffManagement = () => {
  // Mock data for staff members
  const [staff, setStaff] = useState<Staff[]>([
    {
      id: "1",
      name: "John Doe",
      role: "Senior Agent",
      avatar: "https://api.dicebear.com/7.x/avataaars/svg?seed=john",
      status: "available",
      efficiency: 95,
    },
    {
      id: "2",
      name: "Jane Smith",
      role: "Agent",
      avatar: "https://api.dicebear.com/7.x/avataaars/svg?seed=jane",
      status: "busy",
      counter: 2,
      efficiency: 87,
    },
    {
      id: "3",
      name: "Mike Johnson",
      role: "Junior Agent",
      avatar: "https://api.dicebear.com/7.x/avataaars/svg?seed=mike",
      status: "break",
      efficiency: 78,
    },
    {
      id: "4",
      name: "Sarah Williams",
      role: "Senior Agent",
      avatar: "https://api.dicebear.com/7.x/avataaars/svg?seed=sarah",
      status: "available",
      efficiency: 92,
    },
    {
      id: "5",
      name: "Robert Brown",
      role: "Agent",
      avatar: "https://api.dicebear.com/7.x/avataaars/svg?seed=robert",
      status: "offline",
      efficiency: 85,
    },
  ]);

  // Mock data for service counters
  const [counters, setCounters] = useState<Counter[]>([
    {
      id: 1,
      name: "Counter 1",
      serviceType: "General Inquiries",
      status: "open",
    },
    {
      id: 2,
      name: "Counter 2",
      serviceType: "Account Services",
      status: "open",
      assignedStaff: staff[1],
    },
    {
      id: 3,
      name: "Counter 3",
      serviceType: "Technical Support",
      status: "closed",
    },
    {
      id: 4,
      name: "Counter 4",
      serviceType: "Premium Services",
      status: "open",
    },
    {
      id: 5,
      name: "Counter 5",
      serviceType: "General Inquiries",
      status: "maintenance",
    },
  ]);

  // Mock data for shifts
  const [shifts, setShifts] = useState<Shift[]>([
    {
      id: "s1",
      staffId: "1",
      staffName: "John Doe",
      date: new Date(),
      startTime: "08:00",
      endTime: "16:00",
      counter: 1,
    },
    {
      id: "s2",
      staffId: "2",
      staffName: "Jane Smith",
      date: new Date(),
      startTime: "09:00",
      endTime: "17:00",
      counter: 2,
    },
    {
      id: "s3",
      staffId: "4",
      staffName: "Sarah Williams",
      date: new Date(Date.now() + 86400000),
      startTime: "08:00",
      endTime: "16:00",
      counter: 4,
    },
  ]);

  const [selectedDate, setSelectedDate] = useState<Date | undefined>(
    new Date(),
  );

  // Handle drag and drop for staff assignment
  const handleDragEnd = (result: any) => {
    if (!result.destination) return;

    const { source, destination } = result;
    const staffId = result.draggableId;
    const counterId = parseInt(destination.droppableId.replace("counter-", ""));

    // Update staff member's counter assignment
    const updatedStaff = staff.map((s) => {
      if (s.id === staffId) {
        return { ...s, counter: counterId, status: "busy" as const };
      }
      return s;
    });

    // Update counter's assigned staff
    const staffMember = updatedStaff.find((s) => s.id === staffId);
    const updatedCounters = counters.map((c) => {
      if (c.id === counterId) {
        return { ...c, assignedStaff: staffMember };
      }
      // Remove staff from previous counter if they were assigned
      if (c.assignedStaff && c.assignedStaff.id === staffId) {
        return { ...c, assignedStaff: undefined };
      }
      return c;
    });

    setStaff(updatedStaff);
    setCounters(updatedCounters);
  };

  // Get status badge color
  const getStatusColor = (status: string) => {
    switch (status) {
      case "available":
        return "bg-green-500";
      case "busy":
        return "bg-yellow-500";
      case "break":
        return "bg-blue-500";
      case "offline":
        return "bg-gray-500";
      case "open":
        return "bg-green-500";
      case "closed":
        return "bg-red-500";
      case "maintenance":
        return "bg-orange-500";
      default:
        return "bg-gray-500";
    }
  };

  // Filter shifts by selected date
  const filteredShifts = shifts.filter((shift) => {
    if (!selectedDate) return true;
    const shiftDate = new Date(shift.date);
    return shiftDate.toDateString() === selectedDate.toDateString();
  });

  // AI suggestions for staff allocation
  const aiSuggestions = [
    {
      counterId: 1,
      staffId: "4",
      reason: "High efficiency rating (92%) matches with current queue volume",
    },
    {
      counterId: 3,
      staffId: "1",
      reason:
        "Technical expertise needed for pending technical support tickets",
    },
    {
      counterId: 5,
      staffId: "5",
      reason: "Recommended to reopen with experienced staff to handle backlog",
    },
  ];

  return (
    <div className="bg-white p-6 rounded-lg shadow-sm">
      <Tabs defaultValue="assignments" className="w-full">
        <TabsList className="mb-6">
          <TabsTrigger value="assignments">Staff Assignments</TabsTrigger>
          <TabsTrigger value="schedule">Schedule Management</TabsTrigger>
          <TabsTrigger value="performance">Staff Performance</TabsTrigger>
        </TabsList>

        {/* Staff Assignments Tab */}
        <TabsContent value="assignments" className="space-y-6">
          <div className="flex justify-between items-center">
            <h2 className="text-2xl font-bold">Staff Assignments</h2>
            <div className="flex space-x-2">
              <Button variant="outline" size="sm">
                <Clock className="mr-2 h-4 w-4" />
                Auto-Assign
              </Button>
              <Button size="sm">
                <Users className="mr-2 h-4 w-4" />
                Add Staff
              </Button>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Available Staff */}
            <Card>
              <CardHeader>
                <CardTitle>Available Staff</CardTitle>
                <CardDescription>
                  Drag staff to assign to counters
                </CardDescription>
              </CardHeader>
              <CardContent>
                <DragDropContext onDragEnd={handleDragEnd}>
                  <Droppable droppableId="staff-list">
                    {(provided) => (
                      <div
                        {...provided.droppableProps}
                        ref={provided.innerRef}
                        className="space-y-3"
                      >
                        {staff
                          .filter(
                            (s) =>
                              !s.counter ||
                              s.status === "available" ||
                              s.status === "offline",
                          )
                          .map((staffMember, index) => (
                            <Draggable
                              key={staffMember.id}
                              draggableId={staffMember.id}
                              index={index}
                            >
                              {(provided) => (
                                <div
                                  ref={provided.innerRef}
                                  {...provided.draggableProps}
                                  {...provided.dragHandleProps}
                                  className="flex items-center p-3 border rounded-md bg-white hover:bg-gray-50"
                                >
                                  <Avatar className="h-10 w-10 mr-3">
                                    <AvatarImage
                                      src={staffMember.avatar}
                                      alt={staffMember.name}
                                    />
                                    <AvatarFallback>
                                      {staffMember.name.charAt(0)}
                                    </AvatarFallback>
                                  </Avatar>
                                  <div className="flex-1">
                                    <p className="font-medium">
                                      {staffMember.name}
                                    </p>
                                    <p className="text-sm text-gray-500">
                                      {staffMember.role}
                                    </p>
                                  </div>
                                  <Badge
                                    variant="outline"
                                    className={`${getStatusColor(staffMember.status)} text-white`}
                                  >
                                    {staffMember.status}
                                  </Badge>
                                </div>
                              )}
                            </Draggable>
                          ))}
                        {provided.placeholder}
                      </div>
                    )}
                  </Droppable>
                </DragDropContext>
              </CardContent>
            </Card>

            {/* Service Counters */}
            <Card className="col-span-1 lg:col-span-2">
              <CardHeader>
                <CardTitle>Service Counters</CardTitle>
                <CardDescription>Current counter assignments</CardDescription>
              </CardHeader>
              <CardContent>
                <DragDropContext onDragEnd={handleDragEnd}>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {counters.map((counter) => (
                      <Droppable
                        key={counter.id}
                        droppableId={`counter-${counter.id}`}
                      >
                        {(provided) => (
                          <div
                            {...provided.droppableProps}
                            ref={provided.innerRef}
                            className={`border rounded-md p-4 ${counter.status === "maintenance" ? "bg-orange-50" : counter.status === "closed" ? "bg-red-50" : "bg-white"}`}
                          >
                            <div className="flex justify-between items-center mb-3">
                              <h3 className="font-medium">{counter.name}</h3>
                              <Badge
                                variant="outline"
                                className={`${getStatusColor(counter.status)} text-white`}
                              >
                                {counter.status}
                              </Badge>
                            </div>
                            <p className="text-sm text-gray-500 mb-3">
                              {counter.serviceType}
                            </p>

                            {counter.assignedStaff ? (
                              <div className="flex items-center p-3 border rounded-md bg-white">
                                <Avatar className="h-8 w-8 mr-3">
                                  <AvatarImage
                                    src={counter.assignedStaff.avatar}
                                    alt={counter.assignedStaff.name}
                                  />
                                  <AvatarFallback>
                                    {counter.assignedStaff.name.charAt(0)}
                                  </AvatarFallback>
                                </Avatar>
                                <div>
                                  <p className="font-medium">
                                    {counter.assignedStaff.name}
                                  </p>
                                  <p className="text-xs text-gray-500">
                                    {counter.assignedStaff.role}
                                  </p>
                                </div>
                              </div>
                            ) : (
                              <div className="h-16 border border-dashed rounded-md flex items-center justify-center text-gray-400">
                                Drop staff here
                              </div>
                            )}
                            {provided.placeholder}
                          </div>
                        )}
                      </Droppable>
                    ))}
                  </div>
                </DragDropContext>
              </CardContent>
            </Card>

            {/* AI Recommendations */}
            <Card className="col-span-1 lg:col-span-3 bg-blue-50">
              <CardHeader>
                <CardTitle className="flex items-center">
                  <AlertCircle className="mr-2 h-5 w-5 text-blue-600" />
                  AI-Suggested Staff Allocation
                </CardTitle>
                <CardDescription>
                  Based on current queue patterns and staff efficiency
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {aiSuggestions.map((suggestion, index) => {
                    const counter = counters.find(
                      (c) => c.id === suggestion.counterId,
                    );
                    const staffMember = staff.find(
                      (s) => s.id === suggestion.staffId,
                    );

                    if (!counter || !staffMember) return null;

                    return (
                      <div
                        key={index}
                        className="flex items-center justify-between p-3 border rounded-md bg-white"
                      >
                        <div className="flex items-center">
                          <Avatar className="h-8 w-8 mr-3">
                            <AvatarImage
                              src={staffMember.avatar}
                              alt={staffMember.name}
                            />
                            <AvatarFallback>
                              {staffMember.name.charAt(0)}
                            </AvatarFallback>
                          </Avatar>
                          <div>
                            <p className="font-medium">
                              {staffMember.name} → {counter.name}
                            </p>
                            <p className="text-sm text-gray-600">
                              {suggestion.reason}
                            </p>
                          </div>
                        </div>
                        <Button variant="outline" size="sm">
                          Apply
                        </Button>
                      </div>
                    );
                  })}
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Schedule Management Tab */}
        <TabsContent value="schedule" className="space-y-6">
          <div className="flex justify-between items-center">
            <h2 className="text-2xl font-bold">Schedule Management</h2>
            <Button>
              <CalendarIcon className="mr-2 h-4 w-4" />
              Add Shift
            </Button>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Calendar */}
            <Card>
              <CardHeader>
                <CardTitle>Calendar</CardTitle>
                <CardDescription>Select a date to view shifts</CardDescription>
              </CardHeader>
              <CardContent>
                <Calendar
                  mode="single"
                  selected={selectedDate}
                  onSelect={setSelectedDate}
                  className="rounded-md border"
                />
              </CardContent>
            </Card>

            {/* Shifts for Selected Date */}
            <Card className="col-span-1 lg:col-span-2">
              <CardHeader>
                <CardTitle>
                  Shifts for {selectedDate?.toLocaleDateString()}
                </CardTitle>
                <CardDescription>
                  Staff schedule for the selected date
                </CardDescription>
              </CardHeader>
              <CardContent>
                {filteredShifts.length > 0 ? (
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Staff</TableHead>
                        <TableHead>Counter</TableHead>
                        <TableHead>Start Time</TableHead>
                        <TableHead>End Time</TableHead>
                        <TableHead>Actions</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {filteredShifts.map((shift) => (
                        <TableRow key={shift.id}>
                          <TableCell>{shift.staffName}</TableCell>
                          <TableCell>Counter {shift.counter}</TableCell>
                          <TableCell>{shift.startTime}</TableCell>
                          <TableCell>{shift.endTime}</TableCell>
                          <TableCell>
                            <div className="flex space-x-2">
                              <Button variant="outline" size="sm">
                                Edit
                              </Button>
                              <Button
                                variant="outline"
                                size="sm"
                                className="text-red-500"
                              >
                                Delete
                              </Button>
                            </div>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                ) : (
                  <div className="flex flex-col items-center justify-center h-40 text-gray-500">
                    <CalendarIcon className="h-10 w-10 mb-2" />
                    <p>No shifts scheduled for this date</p>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Staff Performance Tab */}
        <TabsContent value="performance" className="space-y-6">
          <div className="flex justify-between items-center">
            <h2 className="text-2xl font-bold">Staff Performance</h2>
            <Select defaultValue="week">
              <SelectTrigger className="w-[180px]">
                <SelectValue placeholder="Time Period" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="day">Today</SelectItem>
                <SelectItem value="week">This Week</SelectItem>
                <SelectItem value="month">This Month</SelectItem>
                <SelectItem value="quarter">This Quarter</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <Card>
            <CardHeader>
              <CardTitle>Performance Metrics</CardTitle>
              <CardDescription>
                Staff efficiency and service metrics
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Staff</TableHead>
                    <TableHead>Role</TableHead>
                    <TableHead>Customers Served</TableHead>
                    <TableHead>Avg. Service Time</TableHead>
                    <TableHead>Efficiency Score</TableHead>
                    <TableHead>Status</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {staff.map((staffMember) => (
                    <TableRow key={staffMember.id}>
                      <TableCell>
                        <div className="flex items-center">
                          <Avatar className="h-8 w-8 mr-2">
                            <AvatarImage
                              src={staffMember.avatar}
                              alt={staffMember.name}
                            />
                            <AvatarFallback>
                              {staffMember.name.charAt(0)}
                            </AvatarFallback>
                          </Avatar>
                          {staffMember.name}
                        </div>
                      </TableCell>
                      <TableCell>{staffMember.role}</TableCell>
                      <TableCell>
                        {Math.floor(Math.random() * 50) + 10}
                      </TableCell>
                      <TableCell>
                        {Math.floor(Math.random() * 5) + 2} mins
                      </TableCell>
                      <TableCell>
                        <div className="flex items-center">
                          <div className="w-full bg-gray-200 rounded-full h-2.5 mr-2">
                            <div
                              className="bg-blue-600 h-2.5 rounded-full"
                              style={{ width: `${staffMember.efficiency}%` }}
                            ></div>
                          </div>
                          <span>{staffMember.efficiency}%</span>
                        </div>
                      </TableCell>
                      <TableCell>
                        <Badge
                          variant="outline"
                          className={`${getStatusColor(staffMember.status)} text-white`}
                        >
                          {staffMember.status}
                        </Badge>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>

          {/* Performance Charts would go here */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle>Service Time Trends</CardTitle>
                <CardDescription>
                  Average service time per staff member
                </CardDescription>
              </CardHeader>
              <CardContent className="h-80 flex items-center justify-center text-gray-500">
                Chart placeholder - Service time trends
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Customer Satisfaction</CardTitle>
                <CardDescription>
                  Feedback scores by staff member
                </CardDescription>
              </CardHeader>
              <CardContent className="h-80 flex items-center justify-center text-gray-500">
                Chart placeholder - Customer satisfaction metrics
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default StaffManagement;
