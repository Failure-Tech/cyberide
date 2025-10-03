"use client";

import React from "react";
import SideBar from "@/app/components/sidebar";
import { useRouter } from "next/navigation";

const Dashboard = () => {
    const router = useRouter();

    return (
        <div className="w-screen flex flex-row bg-white">
        <SideBar selected={1} /> {/* Set selected index for highlighting in sidebar */}

        <div className="grow h-screen flex flex-col px-10 py-8 bg-white gap-6 overflow-y-auto">
            {/* Header */}
            <div className="space-y-2">
            <h1 className="text-4xl font-bold text-black">Dashboard</h1>
            <p className="text-md text-gray-600 max-w-xl">
                Welcome back! Here's an overview of your condrx activity.
            </p>
            </div>

            {/* Stats Section */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-4">
            <div className="bg-gray-50 p-6 rounded-lg shadow-sm border border-gray-200">
                <p className="text-sm text-gray-500">Projects</p>
                <h2 className="text-2xl font-bold text-black mt-1">5</h2>
            </div>
            <div className="bg-gray-50 p-6 rounded-lg shadow-sm border border-gray-200">
                <p className="text-sm text-gray-500">Executions</p>
                <h2 className="text-2xl font-bold text-black mt-1">128</h2>
            </div>
            <div className="bg-gray-50 p-6 rounded-lg shadow-sm border border-gray-200">
                <p className="text-sm text-gray-500">Errors Logged</p>
                <h2 className="text-2xl font-bold text-black mt-1">3</h2>
            </div>
            </div>

            {/* Recent Activity */}
            <div className="mt-8">
            <h2 className="text-xl font-semibold text-gray-800 mb-4">Recent Activity</h2>
            <ul className="space-y-4">
                <li className="bg-white border border-gray-200 p-4 rounded-md shadow-sm">
                <p className="text-gray-700">
                    🐍 You ran <code className="bg-gray-100 px-1 py-0.5 rounded">hello_world.py</code> successfully.
                </p>
                <p className="text-sm text-gray-400 mt-1">2 hours ago</p>
                </li>
                <li className="bg-white border border-gray-200 p-4 rounded-md shadow-sm">
                <p className="text-gray-700">
                    ✏️ Edited <code className="bg-gray-100 px-1 py-0.5 rounded">data_analysis.py</code>.
                </p>
                <p className="text-sm text-gray-400 mt-1">Yesterday</p>
                </li>
            </ul>
            </div>

            {/* Notifications */}
            <div className="mt-8">
            <h2 className="text-xl font-semibold text-gray-800 mb-4">Notifications</h2>
            <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4 rounded-md">
                <p className="text-sm text-yellow-800">You have unused packages in your environment.</p>
            </div>
            </div>

            {/* Quick Actions */}
            <div className="mt-10 grid grid-cols-1 md:grid-cols-2 gap-6">
            <button onClick={() => {router.push("/")}} className="px-6 py-3 bg-black hover:cursor-pointer text-white rounded-md font-medium hover:bg-gray-900 transition">
                ➕ Create New Chat
            </button>
            <button onClick={() => {router.push("/playground")}} className="px-6 py-3 bg-white border hover:cursor-pointer border-gray-300 text-black rounded-md font-medium hover:bg-gray-100 transition">
                🛠️ Manage Projects
            </button>
            </div>
        </div>
        </div>
    );
};

export default Dashboard;
