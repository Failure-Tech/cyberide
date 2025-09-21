import { useAuth } from '../auth/AuthContext'

const Home = () => {
    const { currentUser } = useAuth() || { currentUser: null };
    return (
        <div className='text-2xl font-bold pt-14'>
            {currentUser
                ? <>Hello {currentUser.displayName ? currentUser.displayName : currentUser.email}, you are now logged in.</>
                : <>Hello, you are not logged in.</>
            }
        </div>
    )
}

export default Home